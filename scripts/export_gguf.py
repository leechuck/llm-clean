#!/usr/bin/env python3
"""
Export a fused HuggingFace/MLX model to GGUF format.

Works around a bug in mlx_lm where permute_weights() calls swapaxes(),
producing a non-contiguous array that mx.save_gguf() refuses to serialize
with "can only serialize row-major arrays".

Fix: monkey-patch permute_weights to force a contiguous copy via numpy
before returning, ensuring all arrays are C-contiguous (row-major).

Usage:
    uv run python scripts/export_gguf.py --model /path/to/fused --gguf-path output.gguf
"""

import argparse
import json
import sys
from pathlib import Path


def patch_permute_weights():
    import mlx.core as mx
    import mlx_lm.gguf as gguf_module

    original = gguf_module.permute_weights

    def patched(weights, n_head, n_head_kv=None):
        result = original(weights, n_head, n_head_kv)
        # swapaxes() leaves a non-contiguous view that mx.save_gguf rejects.
        # flatten() returns a 1-D contiguous copy; reshape() back to the
        # original shape produces a row-major (C-contiguous) array.
        # Stays entirely in MLX to avoid numpy bfloat16 buffer issues.
        return result.flatten().reshape(result.shape)

    gguf_module.permute_weights = patched


def main():
    parser = argparse.ArgumentParser(
        description="Export fused model to GGUF (works around mlx_lm row-major bug)"
    )
    parser.add_argument("--model", required=True, help="Path to fused HuggingFace model directory")
    parser.add_argument("--gguf-path", required=True, help="Output GGUF file path")
    args = parser.parse_args()

    model_path = Path(args.model)
    if not model_path.exists():
        print(f"Error: model directory not found: {model_path}", file=sys.stderr)
        sys.exit(1)

    # Apply patch before any mlx_lm imports run the buggy code
    patch_permute_weights()

    import mlx.core as mx
    import mlx_lm.gguf as gguf_module
    from mlx_lm import load
    from mlx.utils import tree_flatten

    print(f"Loading model from {model_path}")
    model, _ = load(str(model_path))
    weights = dict(tree_flatten(model.parameters()))

    with open(model_path / "config.json") as f:
        config = json.load(f)

    print(f"Exporting to {args.gguf_path}")
    gguf_module.convert_to_gguf(str(model_path), weights, config, args.gguf_path)
    print(f"Done: {args.gguf_path}")


if __name__ == "__main__":
    main()
