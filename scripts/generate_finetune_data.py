#!/usr/bin/env python3
"""
Generate fine-tuning data from ground_truth.tsv for local MLX fine-tuning.

This script:
1. Reads ground_truth.tsv (authoritative property labels)
2. Calls a strong LLM to generate reasoning traces for each term
3. Replaces the LLM's predicted properties with ground truth values
4. Outputs finetune_data.jsonl ready for mlx-lm

Usage:
    python scripts/generate_finetune_data.py
    python scripts/generate_finetune_data.py --ground-truth data/raw/ground_truth.tsv
    python scripts/generate_finetune_data.py --model anthropic --output output/data/finetune_data.jsonl
"""

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "src", "llm_clean", "ontology")
)

from analyzer import OntologyAnalyzer
from prompts import ANALYZER_SYSTEM_PROMPT


CLASSIFICATION_RULES = {
    # Rigid Sortals
    ("+R", "+I", "+O"): "Natural Kind",
    ("+R", "+I", "-O"): "Sortal",
    ("+R", "-I", "-O"): "Quality",
    # Anti-Rigid
    ("~R", "+I", "-O"): "Role",
    ("~R", "+I", "+O"): "Role",
    ("~R", "-I", "-O"): "Phase Mixin",
    # Non-Rigid
    ("-R", "+I", "-O"): "Mixin",
    ("-R", "-I", "-O"): "Mixin",
}


def derive_classification(rigidity: str, identity: str, own_identity: str) -> str:
    """Derive classification from meta-property values using OntoClean rules."""
    key = (rigidity, identity, own_identity)
    return CLASSIFICATION_RULES.get(key, "Sortal")


def load_ground_truth(path: str) -> list[dict]:
    """Load ground truth TSV file."""
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(dict(row))
    print(f"Loaded {len(rows)} ground truth examples from {path}")
    return rows


def generate_reasoning(analyzer: OntologyAnalyzer, term: str) -> str:
    """
    Call the LLM to get its reasoning for a term.
    Returns only the reasoning text (we discard its property predictions).
    """
    result = analyzer.analyze(term)
    return result.get("reasoning", "")


def build_jsonl_record(
    term: str,
    rigidity: str,
    identity: str,
    own_identity: str,
    unity: str,
    dependence: str,
    classification: str,
    reasoning: str,
) -> dict:
    """Build a single chat-format JSONL record for mlx-lm instruction tuning."""
    answer = json.dumps(
        {
            "properties": {
                "rigidity": rigidity,
                "identity": identity,
                "own_identity": own_identity,
                "unity": unity,
                "dependence": dependence,
            },
            "classification": classification,
            "reasoning": reasoning,
        },
        indent=2,
    )

    return {
        "messages": [
            {
                "role": "system",
                "content": ANALYZER_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"Term: {term}\nDescription: \nUsage: ",
            },
            {
                "role": "assistant",
                "content": answer,
            },
        ]
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate fine-tuning data from ground_truth.tsv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use Anthropic Claude to generate reasoning (recommended for quality)
  python scripts/generate_finetune_data.py --model anthropic

  # Use Gemini (faster, cheaper)
  python scripts/generate_finetune_data.py --model gemini

  # Custom paths
  python scripts/generate_finetune_data.py \\
      --ground-truth data/raw/ground_truth.tsv \\
      --output output/fine-tunning/data/finetune_data.jsonl \\
      --model anthropic

After running, fine-tune with mlx-lm:
  mlx_lm.lora \\
      --model models/qwen2.5-7b-mlx \\
      --train \\
      --data output/fine-tunning/data/finetune_data.jsonl \\
      --iters 1000 \\
      --adapter-path adapters/qwen7b-ontoclean
        """,
    )

    parser.add_argument(
        "--ground-truth",
        default="data/raw/ground_truth.tsv",
        help="Path to ground_truth.tsv (default: data/raw/ground_truth.tsv)",
    )
    parser.add_argument(
        "--output",
        default="output/fine-tunning/data/finetune_data.jsonl",
        help="Output JSONL file path (default: output/fine-tunning/data/finetune_data.jsonl)",
    )
    parser.add_argument(
        "--model",
        default="gemini",
        help="Model to generate reasoning traces (default: gemini). "
        "Use a strong model for best quality reasoning.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Seconds to wait between API calls to avoid rate limiting (default: 1.0)",
    )
    parser.add_argument(
        "--skip-reasoning",
        action="store_true",
        help="Skip LLM reasoning generation and use empty reasoning strings. "
        "Useful for testing the pipeline without API calls.",
    )

    args = parser.parse_args()

    # Resolve paths relative to project root
    project_root = Path(__file__).parent.parent
    ground_truth_path = project_root / args.ground_truth
    output_path = project_root / args.output

    if not ground_truth_path.exists():
        print(f"Error: ground truth file not found: {ground_truth_path}", file=sys.stderr)
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Fine-Tuning Data Generation")
    print("=" * 60)
    print(f"  Ground truth: {ground_truth_path}")
    print(f"  Output:       {output_path}")
    print(f"  Model:        {args.model}")
    print(f"  Skip reasoning: {args.skip_reasoning}")

    # Load ground truth
    ground_truth = load_ground_truth(str(ground_truth_path))

    # Initialize analyzer (only needed if generating reasoning)
    analyzer = None
    if not args.skip_reasoning:
        print(f"\nInitializing {args.model} analyzer for reasoning generation...")
        try:
            analyzer = OntologyAnalyzer(model=args.model)
        except Exception as e:
            print(f"Error initializing analyzer: {e}", file=sys.stderr)
            print("Try --skip-reasoning to generate data without API calls.", file=sys.stderr)
            sys.exit(1)

    # Generate fine-tuning records
    records = []
    print(f"\nProcessing {len(ground_truth)} terms...")

    for i, row in enumerate(ground_truth):
        term = row["term"]
        rigidity = row["rigidity"]
        identity = row["identity"]
        own_identity = row["own_identity"]
        unity = row["unity"]
        dependence = row["dependence"]

        classification = derive_classification(rigidity, identity, own_identity)

        # Generate reasoning via LLM, or use empty string
        if args.skip_reasoning:
            reasoning = (
                f"{term} has rigidity={rigidity}, identity={identity}, "
                f"own_identity={own_identity}, unity={unity}, dependence={dependence}."
            )
        else:
            print(f"  [{i+1}/{len(ground_truth)}] Generating reasoning for: {term}")
            try:
                reasoning = generate_reasoning(analyzer, term)
            except Exception as e:
                print(f"    Warning: failed to get reasoning for {term}: {e}")
                reasoning = ""

            if args.delay > 0 and i < len(ground_truth) - 1:
                time.sleep(args.delay)

        record = build_jsonl_record(
            term=term,
            rigidity=rigidity,
            identity=identity,
            own_identity=own_identity,
            unity=unity,
            dependence=dependence,
            classification=classification,
            reasoning=reasoning,
        )
        records.append(record)

    # Write JSONL output
    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    print(f"\n✓ Wrote {len(records)} records to {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("Next steps: fine-tune with mlx-lm")
    print("=" * 60)
    print(f"""
1. Download base model; e.g., Qwen/Qwen2.5-7B-Instruct (first time only):
   mlx_lm.convert --hf-path Qwen/Qwen2.5-7B-Instruct \\
       --mlx-path models/qwen2.5-7b-mlx

2. Fine-tune with LoRA:
   mlx_lm.lora \\
       --model models/qwen2.5-7b-mlx \\
       --train \\
       --data {output_path} \\
       --iters 600 \\
       --learning-rate 1e-4 \\
       --lora-layers 8 \\
       --adapter-path adapters/qwen7b-ontoclean

3. Fuse adapter into model:
   mlx_lm.fuse \\
       --model models/qwen2.5-7b-mlx \\
       --adapter-path adapters/qwen7b-ontoclean \\
       --save-path models/qwen7b-ontoclean-fused

4. Convert to GGUF for Ollama:
   python llama.cpp/convert_hf_to_gguf.py models/qwen7b-ontoclean-fused \\
       --outfile models/qwen7b-ontoclean.gguf --outtype q4_k_m

5. Load into Ollama:
   echo 'FROM ./models/qwen7b-ontoclean.gguf' > Modelfile
   ollama create qwen7b-ontoclean -f Modelfile
""")


if __name__ == "__main__":
    main()
