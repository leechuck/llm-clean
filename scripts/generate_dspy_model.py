#!/usr/bin/env python3
"""
Generate an optimized DSPy ontology analysis model using MIPROv2.

This script trains a DSPy model on training data and evaluates it on test data,
using the MIPROv2 optimizer to iteratively improve performance.

Usage:
    python generate_dspy_model.py train.json test.json --output optimized_model
    python generate_dspy_model.py train.tsv test.tsv --output models/guarino_model --model gemini
    python generate_dspy_model.py train.csv test.csv --output model.pkl --auto heavy
"""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to path to import dspy_analyzer
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "src", "llm_clean", "ontology")
)

from dspy_analyzer import DSPyOntologyAnalyzer


def create_metric():
    """
    Create a metric function for evaluating model performance.

    The metric checks how many of the 5 ontological properties match
    between the prediction and the gold example.

    Returns:
        callable: Metric function that returns a score between 0.0 and 1.0
    """

    def ontology_metric(example, prediction, trace=None):
        """
        Calculate the proportion of correct property predictions.

        Args:
            example: Gold standard example with correct properties
            prediction: Model prediction
            trace: Optional trace information (unused)

        Returns:
            float: Score between 0.0 (all wrong) and 1.0 (all correct)
        """
        # Handle both dict and Prediction object
        if hasattr(prediction, "__dict__"):
            pred_dict = {
                "rigidity": prediction.rigidity,
                "identity": prediction.identity,
                "own_identity": prediction.own_identity,
                "unity": prediction.unity,
                "dependence": prediction.dependence,
            }
        else:
            pred_dict = prediction

        # Count matches for each property
        matches = 0
        total = 5

        if pred_dict.get("rigidity") == example.rigidity:
            matches += 1
        if pred_dict.get("identity") == example.identity:
            matches += 1
        if pred_dict.get("own_identity") == example.own_identity:
            matches += 1
        if pred_dict.get("unity") == example.unity:
            matches += 1
        if pred_dict.get("dependence") == example.dependence:
            matches += 1

        # Return proportion correct
        return matches / total

    return ontology_metric


def evaluate_model(analyzer, examples, metric):
    """
    Evaluate the model on a set of examples.

    Args:
        analyzer: DSPyOntologyAnalyzer instance
        examples: List of evaluation examples
        metric: Metric function to use

    Returns:
        dict: Evaluation results with average score and per-example scores
    """
    scores = []

    print(f"\nEvaluating on {len(examples)} examples...")

    for i, example in enumerate(examples):
        # Get model prediction
        result = analyzer.analyze(example.term, description=example.description)

        # Calculate score
        score = metric(example, result, None)
        scores.append(score)

        if (i + 1) % 5 == 0:
            print(f"  Evaluated {i + 1}/{len(examples)} examples...")

    avg_score = sum(scores) / len(scores) if scores else 0.0

    return {"average": avg_score, "scores": scores, "count": len(scores)}


def main():
    parser = argparse.ArgumentParser(
        description="Generate an optimized DSPy ontology analysis model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with JSON files
  python generate_dspy_model.py train.json test.json --output optimized_model
  
  # Use different model with heavy optimization
  python generate_dspy_model.py train.tsv test.tsv \\
      --output models/guarino_gemini \\
      --model gemini \\
      --auto heavy
  
  # Use smaller model for quick training
  python generate_dspy_model.py train.json test.json \\
      --output quick_model \\
      --model llama3b \\
      --auto light
  
  # Full optimization with all parameters
  python generate_dspy_model.py train.csv test.csv \\
      --output final_model \\
      --model anthropic \\
      --auto medium \\
      --max-bootstrapped-demos 4 \\
      --max-labeled-demos 4
        """,
    )

    parser.add_argument("train_file", help="Training data file (TSV, CSV, or JSON)")

    parser.add_argument("test_file", help="Test data file (TSV, CSV, or JSON)")

    parser.add_argument(
        "--output", required=True, help="Output path for the optimized model"
    )

    parser.add_argument(
        "--model",
        default="gemini",
        help="Model to use (default: gemini). Options: gemini, anthropic, gemma9b, qwen7b, llama3b, llama8b",
    )

    parser.add_argument(
        "--auto",
        default="medium",
        choices=["light", "medium", "heavy"],
        help="Optimization mode: light (fast), medium (balanced), heavy (thorough) (default: medium)",
    )

    parser.add_argument(
        "--max-bootstrapped-demos",
        type=int,
        default=4,
        help="Maximum number of bootstrapped demonstrations (default: 4)",
    )

    parser.add_argument(
        "--max-labeled-demos",
        type=int,
        default=4,
        help="Maximum number of labeled demonstrations (default: 4)",
    )

    parser.add_argument(
        "--evaluate-before",
        action="store_true",
        help="Evaluate model before optimization",
    )

    parser.add_argument(
        "--evaluate-after",
        action="store_true",
        help="Evaluate model after optimization",
    )

    args = parser.parse_args()

    # Validate input files exist
    if not os.path.exists(args.train_file):
        print(f"Error: Training file not found: {args.train_file}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.test_file):
        print(f"Error: Test file not found: {args.test_file}", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("DSPy Ontology Model Optimization")
    print("=" * 70)

    print(f"\nConfiguration:")
    print(f"  Training file: {args.train_file}")
    print(f"  Test file: {args.test_file}")
    print(f"  Output path: {args.output}")
    print(f"  Model: {args.model}")
    print(f"  Optimization mode: {args.auto}")
    print(f"  Max bootstrapped demos: {args.max_bootstrapped_demos}")
    print(f"  Max labeled demos: {args.max_labeled_demos}")

    # Initialize analyzer with training and test data
    print("\n" + "=" * 70)
    print("Initializing Analyzer")
    print("=" * 70)

    try:
        analyzer = DSPyOntologyAnalyzer(
            model=args.model, train_file=args.train_file, test_file=args.test_file
        )
    except Exception as e:
        print(f"\nError initializing analyzer: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n✓ Loaded {len(analyzer.train_examples)} training examples")
    print(f"✓ Loaded {len(analyzer.test_examples)} test examples")

    # Create metric
    metric = create_metric()

    # Evaluate before optimization (if requested)
    if args.evaluate_before:
        print("\n" + "=" * 70)
        print("Pre-Optimization Evaluation")
        print("=" * 70)

        results = evaluate_model(analyzer, analyzer.test_examples, metric)
        print(f"\nPre-optimization average score: {results['average']:.3f}")
        print(f"  ({results['average'] * 100:.1f}% of properties correct)")

    # Run optimization
    print("\n" + "=" * 70)
    print("Running MIPROv2 Optimization")
    print("=" * 70)

    print(f"\nThis will take several minutes...")
    print(f"Optimization mode: {args.auto}")
    print("Progress will be shown by the optimizer...\n")

    try:
        optimized_module = analyzer.optimize(
            training_examples=analyzer.train_examples,
            validation_examples=analyzer.test_examples,
            metric=metric,
            auto=args.auto,
            max_bootstrapped_demos=args.max_bootstrapped_demos,
            max_labeled_demos=args.max_labeled_demos,
            save_path=args.output,
        )

        print("\n" + "=" * 70)
        print("✓ Optimization Complete!")
        print("=" * 70)
        print(f"\nOptimized model saved to: {args.output}")

    except Exception as e:
        print(f"\n✗ Error during optimization: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Evaluate after optimization (if requested)
    if args.evaluate_after:
        print("\n" + "=" * 70)
        print("Post-Optimization Evaluation")
        print("=" * 70)

        results = evaluate_model(analyzer, analyzer.test_examples, metric)
        print(f"\nPost-optimization average score: {results['average']:.3f}")
        print(f"  ({results['average'] * 100:.1f}% of properties correct)")

        # Show per-example results
        print(f"\nPer-example scores:")
        for i, (example, score) in enumerate(
            zip(analyzer.test_examples, results["scores"])
        ):
            print(
                f"  {i + 1}. {example.term:20} {score:.2f} ({int(score * 5)}/5 properties)"
            )

    # Final summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    print(f"""
Model Generation Complete!

To use the optimized model:

    from dspy_analyzer import DSPyOntologyAnalyzer
    
    analyzer = DSPyOntologyAnalyzer(
        model="{args.model}",
        optimized_module_path="{args.output}"
    )
    
    result = analyzer.analyze("Student", description="A person enrolled in a university")
    print(result)

The optimized model should perform better than the base model on
similar ontology analysis tasks.
""")


if __name__ == "__main__":
    main()
