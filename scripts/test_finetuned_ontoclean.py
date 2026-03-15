#!/usr/bin/env python3
"""
Test a locally fine-tuned Ollama model against guarino_messy.owl.

Calls any fine-tuned Ollama model (default: mistral7b-ontoclean) for each
entity in guarino_messy.owl, parses its meta-property predictions, and
compares them against ground_truth.tsv.

Usage:
    python scripts/test_finetuned_ontoclean.py
    python scripts/test_finetuned_ontoclean.py --limit 5
    python scripts/test_finetuned_ontoclean.py --model qwen7b-ontoclean
    python scripts/test_finetuned_ontoclean.py --no-compare
    python scripts/test_finetuned_ontoclean.py --output output/finetuned_test.tsv
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import requests
from rdflib import Graph, OWL, RDF, RDFS

# ---------------------------------------------------------------------------
# Paths (resolved relative to project root)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
OWL_FILE     = PROJECT_ROOT / "output/ontologies/guarino_messy.owl"
GROUND_TRUTH = PROJECT_ROOT / "data/raw/ground_truth.tsv"

PROPERTIES   = ["rigidity", "identity", "own_identity", "unity", "dependence"]

SYSTEM_PROMPT = """You are an expert Ontological Analyst specializing in the "Formal Ontology of Properties" methodology by Guarino and Welty (2000).
Analyze the given entity and assign its 5 ontological meta-properties.

The 5 Meta-Properties:
1. Rigidity: +R (Rigid), -R (Non-Rigid), ~R (Anti-Rigid)
2. Identity: +I (carries identity condition), -I (no identity condition)
3. Own Identity: +O (supplies own IC), -O (does not supply own IC)
4. Unity: +U (Unifying), -U (Non-Unifying), ~U (Anti-Unity)
5. Dependence: +D (Dependent), -D (Independent)

Return ONLY valid JSON in this exact format:
{
  "properties": {
    "rigidity": "+R" or "-R" or "~R",
    "identity": "+I" or "-I",
    "own_identity": "+O" or "-O",
    "unity": "+U" or "-U" or "~U",
    "dependence": "+D" or "-D"
  },
  "classification": "Sortal/Role/Mixin/etc",
  "reasoning": "Brief explanation."
}"""

# ---------------------------------------------------------------------------
# Ollama helpers
# ---------------------------------------------------------------------------

def call_ollama(model: str, term: str, description: str = "") -> dict | None:
    """Call the Ollama model and return parsed JSON result, or None on failure."""
    user_content = f"Term: {term}"
    if description:
        user_content += f"\nDescription: {description}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_content},
        ],
        "stream": False,
        "options": {"temperature": 0.1},
    }

    try:
        resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
        resp.raise_for_status()
        content = resp.json()["message"]["content"]
        return parse_response(content)
    except requests.exceptions.ConnectionError:
        print("Error: Ollama not running. Start with: ollama serve", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"  Warning: request failed for '{term}': {e}", file=sys.stderr)
        return None


def parse_response(text: str) -> dict | None:
    """Extract JSON from model response, handling markdown fences."""
    # Strip markdown code fences
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    # Remove trailing commas before } or ]
    text = re.sub(r",\s*([}\]])", r"\1", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON block within response
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


# ---------------------------------------------------------------------------
# OWL extraction
# ---------------------------------------------------------------------------

def load_owl_entities(owl_path: Path) -> list[dict]:
    g = Graph()
    g.parse(str(owl_path))
    entities = []
    for s, _, _ in g.triples((None, RDF.type, OWL.Class)):
        if "#" not in str(s):
            continue
        label = g.value(s, RDFS.label)
        term  = str(label) if label else str(s).split("#")[-1]
        desc  = g.value(s, RDFS.comment)
        entities.append({"term": term, "description": str(desc) if desc else ""})
    return entities


# ---------------------------------------------------------------------------
# Ground truth
# ---------------------------------------------------------------------------

def load_ground_truth(gt_path: Path) -> dict[str, dict]:
    gt = {}
    with open(gt_path, newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            gt[row["term"]] = {p: row[p] for p in PROPERTIES}
    return gt


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score(predicted: dict, gold: dict) -> tuple[int, int]:
    """Return (matches, total) for the five meta-properties."""
    props = predicted.get("properties", {})
    matches = sum(
        1 for p in PROPERTIES
        if props.get(p, "").strip() == gold.get(p, "").strip()
    )
    return matches, len(PROPERTIES)


def render_property(predicted: str, gold: str) -> str:
    """Colour-code a property value: ✓ or ✗."""
    mark = "✓" if predicted.strip() == gold.strip() else "✗"
    return f"{mark} {predicted:<4} (expected {gold})"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Test mistral7b-ontoclean on guarino_messy.owl",
    )
    parser.add_argument("--model",     default="mistral7b-ontoclean",
                        help="Ollama model name (default: mistral7b-ontoclean)")
    parser.add_argument("--owl",       default=str(OWL_FILE),
                        help="Path to OWL file")
    parser.add_argument("--gt",        default=str(GROUND_TRUTH),
                        help="Path to ground_truth.tsv")
    parser.add_argument("--limit",     type=int,
                        help="Analyse only first N entities")
    parser.add_argument("--no-compare", action="store_true",
                        help="Skip ground truth comparison")
    parser.add_argument("--output",    default=None,
                        help="Save results to TSV file")
    args = parser.parse_args()

    # Load data
    entities = load_owl_entities(Path(args.owl))
    if args.limit:
        entities = entities[:args.limit]

    ground_truth = {} if args.no_compare else load_ground_truth(Path(args.gt))

    print(f"\n{'='*60}")
    print(f"  Testing {args.model} on {len(entities)} entities")
    print(f"{'='*60}\n")

    rows = []
    total_matches = total_possible = 0

    for i, entity in enumerate(entities, 1):
        term = entity["term"]
        desc = entity["description"]
        print(f"[{i:2}/{len(entities)}] {term}")

        result = call_ollama(args.model, term, desc)

        if result is None:
            print(f"       ✗ No valid response\n")
            row = {"term": term, **{p: "ERROR" for p in PROPERTIES},
                   "classification": "ERROR", "reasoning": "parse error"}
            rows.append(row)
            continue

        props = result.get("properties", {})
        classification = result.get("classification", "")
        reasoning = result.get("reasoning", "")

        row = {"term": term, **{p: props.get(p, "?") for p in PROPERTIES},
               "classification": classification, "reasoning": reasoning}
        rows.append(row)

        if not args.no_compare and term in ground_truth:
            matches, total = score(result, ground_truth[term])
            total_matches  += matches
            total_possible += total
            pct = matches / total * 100
            print(f"       Score: {matches}/{total} ({pct:.0f}%)")
            for p in PROPERTIES:
                pred = props.get(p, "?")
                gold = ground_truth[term].get(p, "?")
                print(f"         {p:<12} {render_property(pred, gold)}")
        else:
            for p in PROPERTIES:
                print(f"         {p:<12} {props.get(p, '?')}")

        print(f"       class: {classification}")
        print(f"       reason: {reasoning[:120]}{'...' if len(reasoning) > 120 else ''}\n")

    # Summary
    if not args.no_compare and total_possible > 0:
        overall_pct = total_matches / total_possible * 100
        n_compared  = total_possible // len(PROPERTIES)
        print(f"{'='*60}")
        print(f"  Overall: {total_matches}/{total_possible} properties correct")
        print(f"  Accuracy: {overall_pct:.1f}%  ({n_compared} entities compared)")

        # Per-property breakdown
        print(f"\n  Per-property accuracy:")
        for p in PROPERTIES:
            p_matches = sum(
                1 for row in rows
                if row["term"] in ground_truth
                and row.get(p, "?").strip() == ground_truth[row["term"]].get(p, "").strip()
            )
            p_total = sum(1 for row in rows if row["term"] in ground_truth)
            print(f"    {p:<14} {p_matches}/{p_total} ({p_matches/p_total*100:.0f}%)")
        print(f"{'='*60}\n")

    # Save TSV
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", newline="") as f:
            fieldnames = ["term"] + PROPERTIES + ["classification", "reasoning"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)
        print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
