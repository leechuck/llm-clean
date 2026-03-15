#!/usr/bin/env python3
"""
Fine-tune a model locally on Apple Silicon using mlx-lm.

Runs four steps in sequence:
  1. Download & convert base model to MLX format  (skipped if already done)
  2. Fine-tune with LoRA via mlx-lm
  3. Fuse LoRA adapter into model weights and export GGUF  (mlx_lm.fuse --export-gguf)
  4. Register the GGUF as an Ollama model

No llama.cpp installation required — GGUF export is handled by mlx-lm directly.

Usage:
    python scripts/finetune_local.py
    python scripts/finetune_local.py --hf-model Qwen/Qwen2.5-7B-Instruct
    python scripts/finetune_local.py --skip-download --skip-train
    python scripts/finetune_local.py --dry-run
"""

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(cmd: list[str], dry_run: bool = False) -> None:
    """Print and optionally execute a command."""
    print("    $ " + " ".join(str(c) for c in cmd))
    if not dry_run:
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"\nError: command failed with exit code {result.returncode}", file=sys.stderr)
            sys.exit(result.returncode)


def ok(msg: str) -> None:
    print(f"    ✓ {msg}")


def skip(msg: str) -> None:
    print(f"    [skipped] {msg}")


def step(n: int, total: int, title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  Step {n}/{total} — {title}")
    print(f"{'='*60}")


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def step_download(hf_model: str, mlx_path: Path, dry_run: bool) -> None:
    step(1, 4, "Download & convert base model to MLX")
    if mlx_path.exists() and (mlx_path / "config.json").exists():
        skip(f"MLX model already exists at {mlx_path}")
        return
    print(f"    Converting {hf_model} → {mlx_path}  (downloads ~15 GB)")
    run(["mlx_lm.convert", "--hf-path", hf_model, "--mlx-path", str(mlx_path)], dry_run)
    ok(f"Model converted to {mlx_path}")


def prepare_data_dir(data: Path, dry_run: bool) -> Path:
    """
    mlx_lm.lora --data expects a directory containing train.jsonl and valid.jsonl.
    Split the source JSONL 90/10 into that directory and return its path.
    """
    data_dir = data.parent / "mlx_data"
    train_file = data_dir / "train.jsonl"
    valid_file = data_dir / "valid.jsonl"

    if train_file.exists() and valid_file.exists():
        print(f"    Data directory already prepared at {data_dir}")
        return data_dir

    print(f"    Splitting {data.name} → train.jsonl / valid.jsonl (90/10)")
    if not dry_run:
        records = [json.loads(line) for line in data.read_text().splitlines() if line.strip()]
        split = max(1, math.floor(len(records) * 0.9))
        data_dir.mkdir(parents=True, exist_ok=True)
        train_file.write_text("\n".join(json.dumps(r) for r in records[:split]))
        valid_file.write_text("\n".join(json.dumps(r) for r in records[split:]))
        ok(f"train.jsonl: {split} records, valid.jsonl: {len(records) - split} records")
    else:
        print(f"    [dry-run] would write train.jsonl / valid.jsonl to {data_dir}")

    return data_dir


def step_train(
    mlx_path: Path,
    data: Path,
    iters: int,
    lr: str,
    lora_layers: int,
    adapter: Path,
    dry_run: bool,
) -> None:
    step(2, 4, "Fine-tune with LoRA")
    adapter_weights = list(adapter.glob("*.safetensors")) if adapter.exists() else []
    if adapter_weights:
        skip(f"Adapter already exists at {adapter}  (delete to retrain)")
        return
    data_dir = prepare_data_dir(data, dry_run)
    print(f"    Training for {iters} iterations  |  lr={lr}  |  num_layers={lora_layers}")
    run(
        [
            "mlx_lm.lora",
            "--model", str(mlx_path),
            "--train",
            "--data", str(data_dir),
            "--iters", str(iters),
            "--learning-rate", lr,
            "--num-layers", str(lora_layers),
            "--adapter-path", str(adapter),
            "--val-batches", "0",   # disable validation (dataset too small)
        ],
        dry_run,
    )
    ok(f"LoRA adapter saved to {adapter}")


def step_fuse_and_gguf(
    mlx_path: Path, adapter: Path, fused: Path, gguf: Path, dry_run: bool
) -> None:
    """Fuse the LoRA adapter and export GGUF in one mlx_lm.fuse call."""
    step(3, 4, "Fuse adapter and export GGUF")
    if gguf.exists():
        skip(f"GGUF already exists at {gguf}")
        return
    run(
        [
            "mlx_lm.fuse",
            "--model", str(mlx_path),
            "--adapter-path", str(adapter),
            "--save-path", str(fused),
            "--export-gguf",
            "--gguf-path", str(gguf),
        ],
        dry_run,
    )
    ok(f"Fused model saved to {fused}")
    ok(f"GGUF exported to {gguf}")


def step_ollama(gguf: Path, ollama_name: str, dry_run: bool) -> None:
    step(4, 4, "Register with Ollama")
    modelfile = gguf.parent / "Modelfile"
    modelfile_content = f"FROM {gguf.resolve()}\n"

    print(f"    Writing {modelfile}")
    if not dry_run:
        modelfile.write_text(modelfile_content)
    else:
        print(f"    [dry-run] would write: FROM {gguf.resolve()}")

    run(["ollama", "create", ollama_name, "-f", str(modelfile)], dry_run)
    ok(f"Ollama model '{ollama_name}' registered")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    project_root = Path(__file__).parent.parent

    parser = argparse.ArgumentParser(
        description="Fine-tune a model locally on Apple Silicon using mlx-lm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline with defaults
  python scripts/finetune_local.py

  # Resume after training already completed
  python scripts/finetune_local.py --skip-download --skip-train

  # Use a different base model
  python scripts/finetune_local.py \\
    --hf-model mistralai/Mistral-7B-Instruct-v0.3 \\
    --mlx-path models/mistral-7b-mlx \\
    --ollama-name mistral7b-ontoclean

  # Dry run — print commands without executing
  python scripts/finetune_local.py --dry-run

Requirements:
  - macOS with Apple Silicon (M1/M2/M3/M4)
  - mlx-lm  (uv sync, or: pip install mlx-lm)
  - ollama  (https://ollama.com)
        """,
    )

    # Model / path arguments
    parser.add_argument("--hf-model", default="mistralai/Mistral-7B-Instruct-v0.3",
                        help="HuggingFace model ID (default: mistralai/Mistral-7B-Instruct-v0.3 — note: OpenRouter shortcut 'mistral7b' routes to mistralai/mistral-7b-instruct)")
    parser.add_argument("--mlx-path", type=Path,
                        default=project_root / "output/fine-tunning/models/mistral-7b-mlx",
                        help="MLX model output directory (default: output/fine-tunning/models/mistral-7b-mlx)")
    parser.add_argument("--data", type=Path,
                        default=project_root / "output/fine-tunning/data/finetune_data.jsonl",
                        help="Training JSONL file")
    parser.add_argument("--adapter", type=Path,
                        default=project_root / "output/fine-tunning/adapters/mistral7b-ontoclean",
                        help="LoRA adapter output directory (default: output/fine-tunning/adapters/mistral7b-ontoclean)")
    parser.add_argument("--fused", type=Path,
                        default=project_root / "output/fine-tunning/models/mistral7b-ontoclean-fused",
                        help="Fused model output directory (default: output/fine-tunning/models/mistral7b-ontoclean-fused)")
    parser.add_argument("--gguf", type=Path,
                        default=project_root / "output/fine-tunning/models/mistral7b-ontoclean.gguf",
                        help="GGUF output file (default: output/fine-tunning/models/mistral7b-ontoclean.gguf)")
    parser.add_argument("--ollama-name", default="mistral7b-ontoclean",
                        help="Ollama model name (default: mistral7b-ontoclean)")

    # Training hyperparameters
    parser.add_argument("--iters", type=int, default=600,
                        help="LoRA training iterations (default: 600)")
    parser.add_argument("--lr", default="1e-4",
                        help="Learning rate (default: 1e-4)")
    parser.add_argument("--num-layers", type=int, default=8,
                        help="Number of LoRA layers (default: 8)")

    # Skip flags
    parser.add_argument("--skip-download", action="store_true",
                        help="Skip step 1 — model already converted to MLX")
    parser.add_argument("--skip-train", action="store_true",
                        help="Skip step 2 — adapter already trained")
    parser.add_argument("--skip-fuse", action="store_true",
                        help="Skip step 3 — fuse + GGUF export already done")
    parser.add_argument("--skip-ollama", action="store_true",
                        help="Skip step 4 — skip Ollama registration")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print commands without executing them")

    args = parser.parse_args()

    # Resolve paths
    mlx_path = Path(args.mlx_path)
    data     = Path(args.data)
    adapter  = Path(args.adapter)
    fused    = Path(args.fused)
    gguf     = Path(args.gguf)

    # Pre-flight checks
    print("\n" + "="*60)
    print("  Fine-Tuning Pipeline")
    print("="*60)

    if sys.platform != "darwin":
        print("Warning: mlx-lm requires macOS (Apple Silicon). Continuing anyway...", file=sys.stderr)

    if not data.exists():
        print(
            f"\nError: training data not found at '{data}'.\n"
            f"Run first:  uv run scripts/generate_finetune_data.py",
            file=sys.stderr,
        )
        sys.exit(1)

    record_count = sum(1 for _ in data.open())
    print(f"\n  Base model:     {args.hf_model}")
    print(f"  MLX path:       {mlx_path}")
    print(f"  Training data:  {data}  ({record_count} records)")
    print(f"  Adapter:        {adapter}")
    print(f"  Iterations:     {args.iters}  |  lr={args.lr}  |  num_layers={args.num_layers}")
    print(f"  Fused model:    {fused}")
    print(f"  GGUF:           {gguf}")
    print(f"  Ollama name:    {args.ollama_name}")
    if args.dry_run:
        print("\n  *** DRY RUN — commands will be printed but not executed ***")

    # Create output directories
    for d in [mlx_path.parent, adapter.parent, fused.parent, gguf.parent]:
        d.mkdir(parents=True, exist_ok=True)

    # Run steps
    if not args.skip_download:
        step_download(args.hf_model, mlx_path, args.dry_run)
    else:
        step(1, 4, "Download & convert base model to MLX")
        skip("--skip-download passed")

    if not args.skip_train:
        step_train(mlx_path, data, args.iters, args.lr, args.num_layers, adapter, args.dry_run)
    else:
        step(2, 4, "Fine-tune with LoRA")
        skip("--skip-train passed")

    if not args.skip_fuse:
        step_fuse_and_gguf(mlx_path, adapter, fused, gguf, args.dry_run)
    else:
        step(3, 4, "Fuse adapter and export GGUF")
        skip("--skip-fuse passed")

    if not args.skip_ollama:
        step_ollama(gguf, args.ollama_name, args.dry_run)
    else:
        step(4, 4, "Register with Ollama")
        skip("--skip-ollama passed")

    # Summary
    print("\n" + "="*60)
    print("  Pipeline complete!")
    print("="*60)
    if not args.skip_ollama:
        print(f"\n  Test your model:")
        print(f"    ollama run {args.ollama_name}")


if __name__ == "__main__":
    main()
