#!/usr/bin/env python3
"""
Test script for AgentCriticOntologyAnalyzer - demonstrating critic-based validation.
"""
import sys
import os
import json
from git_root import git_root

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_critic_analyzer import AgentCriticOntologyAnalyzer


def test_basic_analysis_with_critic():
    """Test basic analysis with critic validation."""
    print("=" * 60)
    print("Test 1: Basic Analysis WITH Critic Validation")
    print("=" * 60)

    try:
        analyzer = AgentCriticOntologyAnalyzer(
            model="gemini",
            use_default_backgrounds=False,
            max_critique_attempts=3
        )
        result = analyzer.analyze("Student", description="A person enrolled in a university")

        print(f"\nAnalysis of 'Student':")
        print(json.dumps(result, indent=2))

        # Show critique info
        print("\n" + "-" * 40)
        print("Critique Information:")
        print("-" * 40)
        for prop, attempts in result['critique_info'].items():
            print(f"{prop}: {attempts} attempt(s)")
        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_with_default_backgrounds():
    """Test analysis with default property-specific backgrounds and critic validation."""
    print("=" * 60)
    print("Test 2: Analysis WITH Default Backgrounds and Critic")
    print("=" * 60)

    try:
        analyzer = AgentCriticOntologyAnalyzer(
            model="gemini",
            use_default_backgrounds=True,
            default_background_file_type='augmented',
            max_critique_attempts=3
        )
        result = analyzer.analyze("Employee", description="A person working for an organization")

        print(f"\nAnalysis of 'Employee':")
        print(f"Properties: {result['properties']}")
        print(f"Classification: {result['classification']}")

        print("\n" + "-" * 40)
        print("Critique Attempts:")
        print("-" * 40)
        for prop, attempts in result['critique_info'].items():
            print(f"{prop}: {attempts} attempt(s)")

        print("\n" + "-" * 40)
        print("Reasoning:")
        print("-" * 40)
        for prop, reason in result['reasoning'].items():
            print(f"\n{prop.upper()}:")
            print(f"  {reason}")
        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_challenging_term():
    """Test with a term that might require multiple critique attempts."""
    print("=" * 60)
    print("Test 3: Analysis of Challenging Term (may require multiple attempts)")
    print("=" * 60)

    try:
        analyzer = AgentCriticOntologyAnalyzer(
            model="gemini",
            use_default_backgrounds=True,
            max_critique_attempts=3
        )

        # "Red" is often tricky - it's a quality/attribution
        result = analyzer.analyze("Red", description="The color red as a property of objects")

        print(f"\nAnalysis of 'Red':")
        print(f"Properties: {result['properties']}")
        print(f"Classification: {result['classification']}")

        print("\n" + "-" * 40)
        print("Critique Journey:")
        print("-" * 40)
        for prop, attempts in result['critique_info'].items():
            status = "✓ Approved" if attempts <= 1 else f"⚠ Required {attempts} attempts"
            print(f"{prop:15} : {status}")
        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_with_max_attempts():
    """Test behavior when max critique attempts is set low."""
    print("=" * 60)
    print("Test 4: Analysis with Limited Critique Attempts (max=1)")
    print("=" * 60)

    try:
        analyzer = AgentCriticOntologyAnalyzer(
            model="gemini",
            use_default_backgrounds=False,
            max_critique_attempts=1  # Only allow one attempt
        )
        result = analyzer.analyze("Collection", description="A group of items gathered together")

        print(f"\nAnalysis of 'Collection':")
        print(f"Properties: {result['properties']}")
        print(f"Classification: {result['classification']}")

        print("\n" + "-" * 40)
        print("Critique Attempts (max=1):")
        print("-" * 40)
        for prop, attempts in result['critique_info'].items():
            print(f"{prop}: {attempts} attempt(s)")
        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_comparison_with_non_critic():
    """Compare critic vs non-critic analyzer results."""
    print("=" * 60)
    print("Test 5: COMPARISON - Critic vs Non-Critic Analyzer")
    print("=" * 60)

    term = "Student"
    desc = "A person enrolled in a university"

    try:
        # Import the non-critic analyzer for comparison
        from agent_analyzer import AgentOntologyAnalyzer

        print(f"\nAnalyzing '{term}' with BOTH analyzers...")

        # Non-critic version
        print("\n" + "-" * 40)
        print("Without Critic:")
        print("-" * 40)
        analyzer_no_critic = AgentOntologyAnalyzer(
            model="gemini",
            use_default_backgrounds=False
        )
        result_no_critic = analyzer_no_critic.analyze(term, description=desc)
        print(f"Properties: {result_no_critic['properties']}")
        print(f"Classification: {result_no_critic['classification']}")

        # With critic
        print("\n" + "-" * 40)
        print("With Critic:")
        print("-" * 40)
        analyzer_with_critic = AgentCriticOntologyAnalyzer(
            model="gemini",
            use_default_backgrounds=False,
            max_critique_attempts=3
        )
        result_with_critic = analyzer_with_critic.analyze(term, description=desc)
        print(f"Properties: {result_with_critic['properties']}")
        print(f"Classification: {result_with_critic['classification']}")

        # Show critique attempts
        print("\nCritique Attempts:")
        for prop, attempts in result_with_critic['critique_info'].items():
            print(f"  {prop}: {attempts}")

        # Compare properties
        print("\n" + "=" * 40)
        print("PROPERTY COMPARISON:")
        print("=" * 40)
        properties = ['rigidity', 'identity', 'own_identity', 'unity', 'dependence']
        for prop in properties:
            val_no_critic = result_no_critic['properties'].get(prop)
            val_with_critic = result_with_critic['properties'].get(prop)
            if val_no_critic != val_with_critic:
                print(f"{prop:15} | No Critic: {val_no_critic:3} | With Critic: {val_with_critic:3} | DIFFERENT")
            else:
                print(f"{prop:15} | Both: {val_no_critic:3} | SAME")
        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_terms():
    """Test analysis of multiple terms to observe critique patterns."""
    print("=" * 60)
    print("Test 6: Multiple Terms Analysis")
    print("=" * 60)

    terms = [
        ("Person", "A human being"),
        ("Student", "A person enrolled in a university"),
        ("Red", "The color red as a property"),
    ]

    try:
        analyzer = AgentCriticOntologyAnalyzer(
            model="gemini",
            use_default_backgrounds=True,
            max_critique_attempts=3
        )

        results = []
        for term, desc in terms:
            print(f"\nAnalyzing: {term}...")
            result = analyzer.analyze(term, description=desc)
            results.append((term, result))

            # Show brief summary
            print(f"  Classification: {result['classification']}")
            total_attempts = sum(result['critique_info'].values())
            print(f"  Total critique attempts: {total_attempts}")

        # Summary table
        print("\n" + "=" * 60)
        print("SUMMARY TABLE")
        print("=" * 60)
        print(f"{'Term':<15} {'Classification':<30} {'Critique Attempts'}")
        print("-" * 60)
        for term, result in results:
            total = sum(result['critique_info'].values())
            print(f"{term:<15} {result['classification']:<30} {total}")
        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AgentCriticOntologyAnalyzer Test Suite")
    print("=" * 60)
    print("This test suite demonstrates the critic-based validation workflow.")
    print("The critic validates each property analysis and provides feedback")
    print("for re-analysis if needed.")
    print()

    # Run tests
    test_basic_analysis_with_critic()
    print("\n" * 2)

    test_with_default_backgrounds()
    print("\n" * 2)

    test_challenging_term()
    print("\n" * 2)

    test_with_max_attempts()
    print("\n" * 2)

    test_comparison_with_non_critic()
    print("\n" * 2)

    test_multiple_terms()
    print("\n" * 2)

    print("=" * 60)
    print("Tests complete!")
    print("=" * 60)
    print("\nNote: This test requires valid API credentials in .env file")
    print("and will make actual API calls, which may incur costs.")
