#!/usr/bin/env python3
"""
Generate an optimized DSPy agent ontology analysis model.

This script trains a DSPyAgentOntologyAnalyzer on training data and evaluates it
on test data.  Each meta-property is handled by a dedicated ReAct agent, so the
optimized model captures per-property reasoning traces as few-shot demonstrations.

Usage:
    python generate_dspy_agent_model.py train.json test.json --output optimized_agent_model
    python generate_dspy_agent_model.py train.tsv test.tsv --output models/guarino_agent --model gemini
    python generate_dspy_agent_model.py train.json test.json --output model.json --auto heavy
"""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to path to import dspy_agent_analyzer
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "src", "llm_clean", "ontology")
)

from dspy_agent_analyzer import DSPyAgentOntologyAnalyzer


def create_metric():
    """
    Create a metric function for evaluating agent model performance.

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
            prediction: Model prediction (dict or Prediction object)
            trace: Optional trace information (unused)

        Returns:
            float: Score between 0.0 (all wrong) and 1.0 (all correct)
        """
        if hasattr(prediction, "__dict__"):
            pred_dict = {
                "rigidity": getattr(prediction, "rigidity", None),
                "identity": getattr(prediction, "identity", None),
                "own_identity": getattr(prediction, "own_identity", None),
                "unity": getattr(prediction, "unity", None),
                "dependence": getattr(prediction, "dependence", None),
            }
        else:
            pred_dict = prediction

        matches = sum(
            [
                pred_dict.get("rigidity") == getattr(example, "rigidity", None),
                pred_dict.get("identity") == getattr(example, "identity", None),
                pred_dict.get("own_identity") == getattr(example, "own_identity", None),
                pred_dict.get("unity") == getattr(example, "unity", None),
                pred_dict.get("dependence") == getattr(example, "dependence", None),
            ]
        )

        return matches / 5.0

    return ontology_metric


def evaluate_model(analyzer, examples, metric):
    """
    Evaluate the agent model on a set of examples.

    Args:
        analyzer: DSPyAgentOntologyAnalyzer instance
        examples: List of evaluation examples
        metric: Metric function to use

    Returns:
        dict: Evaluation results with average score and per-example scores
    """
    scores = []

    print(f"\nEvaluating on {len(examples)} examples...")

    for i, example in enumerate(examples):
        result = analyzer.analyze(example.term, description=example.description)

        # evaluate_model receives a dict; wrap it to look like a Prediction
        class _Pred:
            pass

        pred = _Pred()
        for prop, val in result["properties"].items():
            setattr(pred, prop, val)

        score = metric(example, pred, None)
        scores.append(score)

        if (i + 1) % 5 == 0:
            print(f"  Evaluated {i + 1}/{len(examples)} examples...")

    avg_score = sum(scores) / len(scores) if scores else 0.0
    return {"average": avg_score, "scores": scores, "count": len(scores)}


def main():
    parser = argparse.ArgumentParser(
        description="Generate an optimized DSPy agent ontology analysis model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with JSON files
  python generate_dspy_agent_model.py train.json test.json --output optimized_agent_model

  # Use Gemini with heavy MIPROv2 optimization
  python generate_dspy_agent_model.py train.tsv test.tsv \\
      --output models/guarino_agent_gemini \\
      --model gemini \\
      --optimizer MIPROv2 \\
      --auto heavy

  # Quick training with a small model
  python generate_dspy_agent_model.py train.json test.json \\
      --output quick_agent_model \\
      --model llama3b \\
      --auto light

  # Full run with pre/post evaluation
  python generate_dspy_agent_model.py train.csv test.csv \\
      --output final_agent_model \\
      --model anthropic \\
      --optimizer BootstrapFewShotWithRandomSearch \\
      --evaluate-before \\
      --evaluate-after
        """,
    )

    parser.add_argument("train_file", help="Training data file (TSV, CSV, or JSON)")
    parser.add_argument("test_file", help="Test data file (TSV, CSV, or JSON)")

    parser.add_argument(
        "--output",
        required=True,
        help="Output path for the optimized agent model",
    )

    parser.add_argument(
        "--model",
        default="llama3b",
        help=(
            "Model to use (default: llama3b). "
            "Shortcuts: gemini, anthropic, gemma9b, qwen7b, llama3b, llama8b, "
            "gpt4o-mini, llama70b, mistral-small-3.1, mistral7b, qwen72b"
        ),
    )

    parser.add_argument(
        "--optimizer",
        default="BootstrapFewShot",
        help=(
            "Optimizer to use (default: BootstrapFewShot, case-insensitive). "
            "Options: BootstrapFewShot, BootstrapFewShotWithRandomSearch, COPRO, MIPROv2."
        ),
    )

    parser.add_argument(
        "--max-bootstrapped-demos",
        type=int,
        default=3,
        help="Maximum number of bootstrapped demonstrations (default: 3)",
    )

    parser.add_argument(
        "--max-labeled-demos",
        type=int,
        default=3,
        help="Maximum number of labeled demonstrations (default: 3)",
    )

    # BootstrapFewShotWithRandomSearch
    parser.add_argument(
        "--num-candidate-programs",
        type=int,
        default=10,
        help="Number of candidate programs (BootstrapFewShotWithRandomSearch only, default: 10)",
    )

    parser.add_argument(
        "--num-threads",
        type=int,
        default=4,
        help="Number of threads (BootstrapFewShotWithRandomSearch / COPRO, default: 4)",
    )

    # COPRO
    parser.add_argument(
        "--breadth",
        type=int,
        default=10,
        help="COPRO breadth parameter (default: 10)",
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=3,
        help="COPRO depth parameter (default: 3)",
    )

    parser.add_argument(
        "--init-temperature",
        type=float,
        default=1.0,
        help="COPRO initial temperature (default: 1.0)",
    )

    # MIPROv2
    parser.add_argument(
        "--auto",
        default="medium",
        choices=["light", "medium", "heavy"],
        help="MIPROv2 optimization mode (default: medium)",
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

    # Validate input files
    if not os.path.exists(args.train_file):
        print(f"Error: Training file not found: {args.train_file}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.test_file):
        print(f"Error: Test file not found: {args.test_file}", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("DSPy Agent Ontology Model Optimization")
    print("=" * 70)

    print(f"\nConfiguration:")
    print(f"  Training file:          {args.train_file}")
    print(f"  Test file:              {args.test_file}")
    print(f"  Output path:            {args.output}")
    print(f"  Model:                  {args.model}")
    print(f"  Optimizer:              {args.optimizer}")
    if args.optimizer == "MIPROv2":
        print(f"  Optimization mode:      {args.auto}")
    print(f"  Max bootstrapped demos: {args.max_bootstrapped_demos}")
    print(f"  Max labeled demos:      {args.max_labeled_demos}")

    # Initialize analyzer
    print("\n" + "=" * 70)
    print("Initializing Agent Analyzer")
    print("=" * 70)

    try:
        analyzer = DSPyAgentOntologyAnalyzer(
            model=args.model,
            train_file=args.train_file,
            test_file=args.test_file,
        )
    except Exception as e:
        print(f"\nError initializing analyzer: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n✓ Loaded {len(analyzer.train_examples)} training examples")
    print(f"✓ Loaded {len(analyzer.test_examples)} test examples")

    metric = create_metric()

    # Pre-optimization evaluation
    if args.evaluate_before:
        print("\n" + "=" * 70)
        print("Pre-Optimization Evaluation")
        print("=" * 70)
        results = evaluate_model(analyzer, analyzer.test_examples, metric)
        print(f"\nPre-optimization average score: {results['average']:.3f}")
        print(f"  ({results['average'] * 100:.1f}% of properties correct)")

    # Run optimization
    print("\n" + "=" * 70)
    print(f"Running {args.optimizer} Optimization")
    print("=" * 70)
    print(f"\nThis will take several minutes...")
    print("Progress will be shown by the optimizer...\n")

    try:
        opt_kwargs = {
            "training_examples": analyzer.train_examples,
            "validation_examples": analyzer.test_examples,
            "metric": metric,
            "optimizer": args.optimizer,
            "max_bootstrapped_demos": args.max_bootstrapped_demos,
            "max_labeled_demos": args.max_labeled_demos,
            "save_path": args.output,
        }

        if args.optimizer == "BootstrapFewShotWithRandomSearch":
            opt_kwargs["num_candidate_programs"] = args.num_candidate_programs
            opt_kwargs["num_threads"] = args.num_threads
        elif args.optimizer == "COPRO":
            opt_kwargs["breadth"] = args.breadth
            opt_kwargs["depth"] = args.depth
            opt_kwargs["init_temperature"] = args.init_temperature
            opt_kwargs["num_threads"] = args.num_threads
        elif args.optimizer == "MIPROv2":
            opt_kwargs["auto"] = args.auto

        optimized_module = analyzer.optimize(**opt_kwargs)

        print("\n" + "=" * 70)
        print("✓ Optimization Complete!")
        print("=" * 70)
        print(f"\nOptimized model saved to: {args.output}")

    except Exception as e:
        print(f"\n✗ Error during optimization: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Post-optimization evaluation
    if args.evaluate_after:
        print("\n" + "=" * 70)
        print("Post-Optimization Evaluation")
        print("=" * 70)
        results = evaluate_model(analyzer, analyzer.test_examples, metric)
        print(f"\nPost-optimization average score: {results['average']:.3f}")
        print(f"  ({results['average'] * 100:.1f}% of properties correct)")

        print(f"\nPer-example scores:")
        for i, (example, score) in enumerate(
            zip(analyzer.test_examples, results["scores"])
        ):
            print(
                f"  {i + 1}. {example.term:20} {score:.2f} ({int(score * 5)}/5 properties)"
            )

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    print(f"""
Agent Model Generation Complete!

To use the optimized model:

    from dspy_agent_analyzer import DSPyAgentOntologyAnalyzer

    analyzer = DSPyAgentOntologyAnalyzer(
        model="{args.model}",
        optimized_module_path="{args.output}"
    )

    result = analyzer.analyze("Student", description="A person enrolled in a university")
    print(result)

The optimized agent model uses per-property ReAct agents with bootstrapped
few-shot demonstrations to improve ontological analysis accuracy.
""")


if __name__ == "__main__":
    main()
