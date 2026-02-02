#!/usr/bin/env python3
"""
Compare standard OntologyAnalyzer vs AgentOntologyAnalyzer results.
"""
import argparse
import sys
import os
import json
import time

# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology_tools.analyzer import OntologyAnalyzer
from ontology_tools.agent_analyzer import AgentOntologyAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="Compare standard vs agent-based ontology analysis"
    )
    parser.add_argument("term", help="The entity term to analyze.")
    parser.add_argument("--desc", help="Additional description of the entity.")
    parser.add_argument("--usage", help="Example usage context.")
    parser.add_argument("--model", default="gemini",
                       help="Model to use (default: gemini)")
    parser.add_argument("--background-file", dest="background_file",
                       help="Background file to use for both analyzers")
    parser.add_argument("--no-default-backgrounds", dest="no_default_backgrounds",
                       action="store_true",
                       help="Disable default property-specific backgrounds for agent analyzer")
    parser.add_argument("--output", "-o",
                       help="Output file for comparison results (JSON)")

    args = parser.parse_args()

    print("=" * 70)
    print("COMPARISON: Standard vs Agent-Based Ontology Analysis")
    print("=" * 70)
    print(f"Term: {args.term}")
    if args.desc:
        print(f"Description: {args.desc}")
    print(f"Model: {args.model}")
    if args.background_file:
        print(f"Background: {args.background_file}")
    print("=" * 70)
    print()

    results = {
        "term": args.term,
        "description": args.desc,
        "model": args.model,
        "background_file": args.background_file,
        "standard": {},
        "agent_based": {},
        "comparison": {}
    }

    # Standard Analyzer
    print("Running STANDARD analyzer...")
    print("-" * 70)
    start_time = time.time()
    try:
        standard_analyzer = OntologyAnalyzer(
            model=args.model,
            background_file=args.background_file
        )
        standard_result = standard_analyzer.analyze(args.term, args.desc, args.usage)
        standard_time = time.time() - start_time

        results["standard"] = {
            "result": standard_result,
            "time_seconds": standard_time,
            "api_calls": 1
        }

        print(f"✓ Completed in {standard_time:.2f} seconds")
        print(f"Properties: {standard_result['properties']}")
        print(f"Classification: {standard_result['classification']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        results["standard"] = {"error": str(e)}
        import traceback
        traceback.print_exc()

    print()

    # Agent-Based Analyzer
    print("Running AGENT-BASED analyzer...")
    print("-" * 70)
    start_time = time.time()
    try:
        agent_analyzer = AgentOntologyAnalyzer(
            model=args.model,
            default_background_file=args.background_file,
            use_default_backgrounds=not args.no_default_backgrounds
        )
        agent_result = agent_analyzer.analyze(args.term, args.desc, args.usage)
        agent_time = time.time() - start_time

        results["agent_based"] = {
            "result": agent_result,
            "time_seconds": agent_time,
            "api_calls": 5
        }

        print(f"✓ Completed in {agent_time:.2f} seconds")
        print(f"Properties: {agent_result['properties']}")
        print(f"Classification: {agent_result['classification']}")
    except Exception as e:
        print(f"✗ Error: {e}")
        results["agent_based"] = {"error": str(e)}
        import traceback
        traceback.print_exc()

    print()
    print("=" * 70)
    print("COMPARISON RESULTS")
    print("=" * 70)

    if "error" not in results["standard"] and "error" not in results["agent_based"]:
        # Compare properties
        standard_props = results["standard"]["result"]["properties"]
        agent_props = results["agent_based"]["result"]["properties"]

        print("\nProperty-by-Property Comparison:")
        print(f"{'Property':<15} | {'Standard':<10} | {'Agent-Based':<12} | {'Match':<6}")
        print("-" * 70)

        differences = []
        for prop in ["rigidity", "identity", "own_identity", "unity", "dependence"]:
            std_val = standard_props.get(prop, "N/A")
            agent_val = agent_props.get(prop, "N/A")
            match = "✓" if std_val == agent_val else "✗"

            if std_val != agent_val:
                differences.append(prop)

            print(f"{prop:<15} | {std_val:<10} | {agent_val:<12} | {match:<6}")

        results["comparison"]["property_differences"] = differences
        results["comparison"]["agreement_rate"] = (5 - len(differences)) / 5

        print(f"\nAgreement Rate: {results['comparison']['agreement_rate']*100:.1f}%")
        print(f"Differences in: {', '.join(differences) if differences else 'None'}")

        # Compare classifications
        std_class = results["standard"]["result"]["classification"]
        agent_class = results["agent_based"]["result"]["classification"]
        print(f"\nClassification:")
        print(f"  Standard:    {std_class}")
        print(f"  Agent-Based: {agent_class}")
        print(f"  Match: {'✓' if std_class == agent_class else '✗'}")

        results["comparison"]["classification_match"] = (std_class == agent_class)

        # Compare performance
        std_time = results["standard"]["time_seconds"]
        agent_time = results["agent_based"]["time_seconds"]
        print(f"\nPerformance:")
        print(f"  Standard:    {std_time:.2f}s (1 API call)")
        print(f"  Agent-Based: {agent_time:.2f}s (5 API calls)")
        print(f"  Slowdown:    {agent_time/std_time:.2f}x")

        results["comparison"]["time_ratio"] = agent_time / std_time

        # Show reasoning differences if they disagree
        if differences:
            print(f"\nDetailed Reasoning for Differences:")
            print("-" * 70)
            for prop in differences:
                print(f"\n{prop.upper()}:")
                print(f"  Standard:    {std_val}")
                print(f"               {results['standard']['result'].get('reasoning', 'N/A')}")
                print(f"  Agent-Based: {agent_val}")
                if 'reasoning' in results['agent_based']['result']:
                    print(f"               {results['agent_based']['result']['reasoning'].get(prop, 'N/A')}")

    else:
        print("Cannot compare: One or both analyzers encountered errors")

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to: {args.output}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
