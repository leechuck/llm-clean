#!/usr/bin/env python3
"""
Test script demonstrating the DSPyOntologyAnalyzer with optimization.

This script shows how to:
1. Use the basic analyzer
2. Create training examples
3. Optimize the analyzer using MIPROv2
4. Evaluate the optimized model
"""

import sys
import os
import json
from git_root import git_root

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dspy_analyzer import DSPyOntologyAnalyzer


def test_basic_analysis():
    """Test basic analysis without optimization."""
    print("=" * 60)
    print("Test 1: Basic Analysis (No Optimization)")
    print("=" * 60)

    try:
        analyzer = DSPyOntologyAnalyzer(model="gemini")

        # Test a few entities
        test_cases = [
            ("Student", "A person enrolled in a university"),
            ("Person", "A human being"),
            ("Red", "The color red, as a property of objects"),
        ]

        for term, desc in test_cases:
            print(f"\nAnalyzing '{term}'...")
            result = analyzer.analyze(term, description=desc)
            print(f"  Rigidity: {result['properties']['rigidity']}")
            print(f"  Identity: {result['properties']['identity']}")
            print(f"  Own Identity: {result['properties']['own_identity']}")
            print(f"  Unity: {result['properties']['unity']}")
            print(f"  Dependence: {result['properties']['dependence']}")
            print(f"  Classification: {result['classification']}")
            print(f"  Reasoning: {result['reasoning'][:100]}...")

        print("\n✓ Basic analysis test completed")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


def test_optimization():
    """Test optimization with training examples."""
    print("\n" + "=" * 60)
    print("Test 2: Optimization with MIPROv2")
    print("=" * 60)

    try:
        analyzer = DSPyOntologyAnalyzer(model="gemini")

        # Create training examples based on known correct analyses
        print("\nCreating training examples...")
        training_examples = [
            # Student - Role (Anti-rigid, dependent)
            analyzer.create_example(
                term="Student",
                description="A person enrolled in a university",
                rigidity="~R",
                identity="+I",
                own_identity="-O",
                unity="+U",
                dependence="+D",
                classification="Role (Anti-rigid, dependent)",
            ),
            # Person - Sortal (Rigid, supplies identity)
            analyzer.create_example(
                term="Person",
                description="A human being",
                rigidity="+R",
                identity="+I",
                own_identity="+O",
                unity="+U",
                dependence="-D",
                classification="Sortal (Rigid, supplies identity)",
            ),
            # Red - Attribution (Non-rigid, no identity)
            analyzer.create_example(
                term="Red",
                description="The color red, as a property of objects",
                rigidity="-R",
                identity="-I",
                own_identity="-O",
                unity="-U",
                dependence="-D",
                classification="Attribution (Non-rigid, no identity)",
            ),
            # Employee - Role (Anti-rigid, dependent)
            analyzer.create_example(
                term="Employee",
                description="A person working for an organization",
                rigidity="~R",
                identity="+I",
                own_identity="-O",
                unity="+U",
                dependence="+D",
                classification="Role (Anti-rigid, dependent)",
            ),
            # Car - Sortal (Rigid, carries identity)
            analyzer.create_example(
                term="Car",
                description="A four-wheeled motor vehicle",
                rigidity="+R",
                identity="+I",
                own_identity="+O",
                unity="+U",
                dependence="-D",
                classification="Sortal (Rigid, supplies identity)",
            ),
        ]

        print(f"Created {len(training_examples)} training examples")

        # Note: MIPROv2 optimization can take a while and requires multiple API calls
        # For a quick test, we use a small number of trials
        print("\nOptimizing with MIPROv2 (this may take a few minutes)...")
        print("Note: Using only 10 trials for quick testing")
        print("For production, increase num_trials to 50+ for better results")

        optimized = analyzer.optimize(
            training_examples=training_examples,
            num_trials=10,  # Use more trials (50+) for production
            max_bootstrapped_demos=3,
            max_labeled_demos=3,
            save_path="dspy_optimized_ontology_analyzer",
        )

        print("\n✓ Optimization completed!")
        print("✓ Optimized model saved to 'dspy_optimized_ontology_analyzer'")

        # Test the optimized model
        print("\n" + "=" * 60)
        print("Testing optimized model on new example...")
        print("=" * 60)

        result = analyzer.analyze(
            "Teacher", description="A person who teaches students in a school"
        )

        print("\nAnalysis of 'Teacher':")
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


def test_load_optimized():
    """Test loading a previously optimized model."""
    print("\n" + "=" * 60)
    print("Test 3: Loading Optimized Model")
    print("=" * 60)

    optimized_path = "dspy_optimized_ontology_analyzer"

    if not os.path.exists(optimized_path):
        print(f"⚠ Optimized model not found at {optimized_path}")
        print("Run test_optimization() first to create an optimized model")
        return

    try:
        print(f"\nLoading optimized model from {optimized_path}...")
        analyzer = DSPyOntologyAnalyzer(
            model="gemini", optimized_module_path=optimized_path
        )

        print("✓ Optimized model loaded successfully")

        # Test the loaded model
        result = analyzer.analyze(
            "Doctor", description="A person licensed to practice medicine"
        )

        print("\nAnalysis of 'Doctor' using optimized model:")
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


def show_comparison():
    """Compare results before and after optimization."""
    print("\n" + "=" * 60)
    print("Test 4: Comparison - Before vs After Optimization")
    print("=" * 60)

    optimized_path = "dspy_optimized_ontology_analyzer"

    if not os.path.exists(optimized_path):
        print(f"⚠ Optimized model not found. Skipping comparison.")
        return

    try:
        # Test term
        term = "Professor"
        desc = "A senior teacher at a university"

        # Unoptimized
        print(f"\nAnalyzing '{term}' with UNOPTIMIZED model...")
        analyzer_basic = DSPyOntologyAnalyzer(model="gemini")
        result_basic = analyzer_basic.analyze(term, description=desc)

        # Optimized
        print(f"Analyzing '{term}' with OPTIMIZED model...")
        analyzer_opt = DSPyOntologyAnalyzer(
            model="gemini", optimized_module_path=optimized_path
        )
        result_opt = analyzer_opt.analyze(term, description=desc)

        # Compare
        print("\n" + "=" * 40)
        print("COMPARISON:")
        print("=" * 40)

        properties = ["rigidity", "identity", "own_identity", "unity", "dependence"]
        for prop in properties:
            basic_val = result_basic["properties"][prop]
            opt_val = result_opt["properties"][prop]
            match = "✓" if basic_val == opt_val else "✗"
            print(f"{match} {prop:15} | Basic: {basic_val:3} | Optimized: {opt_val:3}")

        print(f"\nBasic Classification: {result_basic['classification']}")
        print(f"Optimized Classification: {result_opt['classification']}")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DSPyOntologyAnalyzer Test Suite")
    print("=" * 60)
    print()

    # Run tests
    test_basic_analysis()
    print("\n" * 2)

    # Note: Optimization can be expensive (many API calls)
    # Uncomment to run optimization tests
    # test_optimization()
    # print("\n" * 2)

    # test_load_optimized()
    # print("\n" * 2)

    # show_comparison()
    # print("\n" * 2)

    print("\n" + "=" * 60)
    print("Tests complete!")
    print("\nTo run optimization tests, uncomment the test functions in __main__")
    print("Note: Optimization requires multiple API calls and may take several minutes")
    print("=" * 60)
