#!/usr/bin/env python3
"""
Batch analyze entities from an OWL file using DSPy-optimized analyzer.

This script extracts classes from an OWL ontology file and analyzes each
using a trained DSPy model for improved accuracy through optimization.

Usage:
    # Using a pre-trained model
    python batch_analyze_dspy.py input.owl --compiled-model models/optimized.json --output results.tsv

    # Using base model (no optimization)
    python batch_analyze_dspy.py input.owl --model llama3b --output results.tsv

    # With training data for runtime optimization
    python batch_analyze_dspy.py input.owl --train-file train.tsv --optimize-mode medium --output results.tsv
"""

# Ensure the project root is in sys.path
import sys, os, pathlib
from git_root import git_root

sys.path.append(str(pathlib.Path(git_root())))

import argparse
import json
import csv
from rdflib import Graph, RDF, OWL, RDFS
from src.llm_clean.ontology.dspy_analyzer import DSPyOntologyAnalyzer


def extract_classes(owl_path):
    """
    Extract OWL classes from an ontology file.

    Args:
        owl_path: Path to the OWL file

    Returns:
        List of dicts with uri, term, and description for each class
    """
    g = Graph()
    g.parse(owl_path)

    classes = []
    for s, p, o in g.triples((None, RDF.type, OWL.Class)):
        # Extract label or use local name
        label = g.value(s, RDFS.label)
        if not label:
            # simple local name extraction from URI
            if "#" in str(s):
                label = str(s).split("#")[-1]
            else:
                label = str(s).split("/")[-1]

        # Extract comment/description if available
        comment = g.value(s, RDFS.comment)

        classes.append(
            {
                "uri": str(s),
                "term": str(label),
                "description": str(comment) if comment else None,
            }
        )
    return classes


def main():
    parser = argparse.ArgumentParser(
        description="Batch analyze entities from an OWL file using DSPy-optimized analyzer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use a pre-trained optimized model
  python batch_analyze_dspy.py input.owl \\
      --compiled-model output/models/optimized_llama3b.json \\
      --model llama3b \\
      --output results.tsv
  
  # Use base model without optimization
  python batch_analyze_dspy.py input.owl \\
      --model llama8b \\
      --output results.json \\
      --format json
  
  # Optimize at runtime with training data
  python batch_analyze_dspy.py input.owl \\
      --train-file output/train_test_sets/data_train.tsv \\
      --test-file output/train_test_sets/data_test.tsv \\
      --optimize-mode medium \\
      --output results.tsv
  
  # Test with limited entities
  python batch_analyze_dspy.py input.owl \\
      --compiled-model models/optimized.json \\
      --limit 5
        """,
    )

    parser.add_argument("input_owl", help="Path to the input OWL file")

    parser.add_argument(
        "--format",
        choices=["tsv", "json"],
        default="tsv",
        help="Output format (tsv or json, default: tsv)",
    )

    parser.add_argument("--output", help="Output file path (default: stdout)")

    parser.add_argument(
        "--limit", type=int, help="Limit number of classes to analyze (for testing)"
    )

    parser.add_argument(
        "--model",
        default="llama3b",
        help="Model to use (default: llama3b). Options: llama3b, llama8b, gemini, anthropic, gemma9b, qwen7b",
    )

    parser.add_argument(
        "--compiled-model",
        dest="compiled_model_path",
        help="Path to pre-trained/optimized DSPy model (JSON file)",
    )

    parser.add_argument(
        "--train-file",
        dest="train_file",
        help="Path to training data file (TSV, CSV, or JSON) for runtime optimization",
    )

    parser.add_argument(
        "--test-file",
        dest="test_file",
        help="Path to test data file (TSV, CSV, or JSON) for evaluation during optimization",
    )

    parser.add_argument(
        "--optimize-mode",
        dest="optimize_mode",
        choices=["light", "medium", "heavy"],
        help="Optimization mode (light, medium, heavy). Only used with --train-file",
    )

    args = parser.parse_args()
    args.input_owl = os.path.abspath(args.input_owl)

    # Strip the "dspy_" prefix that the Makefile adds to model names for
    # output-file/agent-name labelling — the analyzer only knows bare shortcuts.
    if args.model.startswith("dspy_"):
        args.model = args.model[len("dspy_") :]

    # Validate arguments
    if args.optimize_mode and not args.train_file:
        print("Error: --optimize-mode requires --train-file", file=sys.stderr)
        sys.exit(1)

    # Extract classes from OWL file
    print(f"Loading OWL file: {args.input_owl}", file=sys.stderr)
    try:
        classes = extract_classes(args.input_owl)
    except Exception as e:
        print(f"Error loading OWL file: {e}", file=sys.stderr)
        sys.exit(1)

    # Limit classes if requested
    if args.limit:
        classes = classes[: args.limit]
        print(f"Limiting analysis to first {args.limit} classes", file=sys.stderr)

    # Initialize DSPy analyzer
    print(f"Initializing DSPy analyzer (model: {args.model})...", file=sys.stderr)
    try:
        analyzer = DSPyOntologyAnalyzer(
            model=args.model,
            optimized_module_path=args.compiled_model_path,
            train_file=args.train_file,
            test_file=args.test_file,
        )

        # Run optimization if requested
        if args.optimize_mode and args.train_file:
            print(
                f"Running optimization (mode: {args.optimize_mode})...", file=sys.stderr
            )
            print("This may take several minutes...", file=sys.stderr)
            analyzer.optimize(
                training_examples=analyzer.train_examples,
                validation_examples=analyzer.test_examples,
                auto=args.optimize_mode,
            )
            print("Optimization complete!", file=sys.stderr)

    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Initialization Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Analyze each class
    results = []
    total = len(classes)
    print(f"\nFound {total} classes. Starting analysis...", file=sys.stderr)

    for i, cls in enumerate(classes):
        term = cls["term"]
        desc = cls["description"]
        print(f"[{i + 1}/{total}] Analyzing: {term}", file=sys.stderr)

        try:
            # Analyze using DSPy
            analysis = analyzer.analyze(term, description=desc or "")

            # Extract properties from nested structure
            props = analysis.get("properties", {})

            row = {
                "term": term,
                "uri": cls["uri"],
                "rigidity": props.get("rigidity", "N/A"),
                "identity": props.get("identity", "N/A"),
                "own_identity": props.get("own_identity", "N/A"),
                "unity": props.get("unity", "N/A"),
                "dependence": props.get("dependence", "N/A"),
                "classification": analysis.get("classification", "N/A"),
                "reasoning": analysis.get("reasoning", "N/A"),
            }
            results.append(row)

        except Exception as e:
            print(f"Failed to analyze '{term}': {e}", file=sys.stderr)
            results.append(
                {
                    "term": term,
                    "uri": cls["uri"],
                    "error": str(e),
                    "rigidity": "ERROR",
                    "identity": "ERROR",
                    "own_identity": "ERROR",
                    "unity": "ERROR",
                    "dependence": "ERROR",
                    "classification": "ERROR",
                    "reasoning": f"Analysis failed: {e}",
                }
            )

    # Output results
    print(f"\nAnalysis complete! Writing results...", file=sys.stderr)

    if args.output:
        args.output = os.path.abspath(args.output)
        out_stream = open(args.output, "w", newline="", encoding="utf-8")
        print(f"Output file: {args.output}", file=sys.stderr)
    else:
        out_stream = sys.stdout

    try:
        if args.format == "json":
            json.dump(results, out_stream, indent=2)
        else:
            fieldnames = [
                "term",
                "uri",
                "rigidity",
                "identity",
                "own_identity",
                "unity",
                "dependence",
                "classification",
                "reasoning",
                "error",
            ]
            writer = csv.DictWriter(
                out_stream, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(results)
    finally:
        if args.output:
            out_stream.close()

    print(f"✓ Successfully analyzed {len(results)} classes", file=sys.stderr)


if __name__ == "__main__":
    main()
