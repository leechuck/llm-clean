#!/usr/bin/env python3
"""
Test script for DSPyAgentOntologyAnalyzer.

Tests the agent-based DSPy analyzer where each meta-property is evaluated
by a dedicated ReAct agent.

Tests:
1. Basic analysis        – run the five property agents on a handful of terms
2. Agent tools           – call the standalone tool functions directly
3. Constraint checking   – verify the +O → +I constraint tool works correctly
4. Optimization          – bootstrap few-shot on a small training set (optional)
"""

import sys
import os
import json

# Allow running directly from this directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dspy_agent_analyzer import (
    DSPyAgentOntologyAnalyzer,
    initiate_task,
    get_property_definition,
    get_property_examples,
    check_constraints,
)

PROPERTIES = ["rigidity", "identity", "own_identity", "unity", "dependence"]

VALID_VALUES = {
    "rigidity": {"+R", "-R", "~R"},
    "identity": {"+I", "-I"},
    "own_identity": {"+O", "-O"},
    "unity": {"+U", "-U", "~U"},
    "dependence": {"+D", "-D"},
}


# ---------------------------------------------------------------------------
# Test 1: Basic analysis
# ---------------------------------------------------------------------------


def test_basic_analysis():
    """Run the full agent pipeline on several well-known ontological entities."""
    print("=" * 60)
    print("Test 1: Basic Analysis")
    print("=" * 60)

    try:
        analyzer = DSPyAgentOntologyAnalyzer(model="gemini")

        test_cases = [
            ("Student", "A person enrolled in a university"),
            ("Person", "A human being"),
            ("Red", "The color red, as a property of objects"),
            ("Employee", "A person working for an organisation"),
        ]

        for term, desc in test_cases:
            print(f"\nAnalyzing '{term}'...")
            result = analyzer.analyze(term, description=desc)

            props = result["properties"]
            for prop in PROPERTIES:
                value = props[prop]
                valid = value in VALID_VALUES[prop]
                marker = "✓" if valid else "✗"
                print(f"  {marker} {prop:15}: {value}")
                if not valid:
                    print(
                        f"      WARNING: '{value}' is not a recognised value "
                        f"for {prop} {VALID_VALUES[prop]}"
                    )

            print(f"  Classification : {result['classification']}")
            print(f"  Reasoning      : {result['reasoning'][:120]}...")

        print("\n✓ Basic analysis test completed")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


# ---------------------------------------------------------------------------
# Test 2: Agent tools (unit-level, no LLM call)
# ---------------------------------------------------------------------------


def test_agent_tools():
    """Call the ontology tool functions directly to verify they return content."""
    print("\n" + "=" * 60)
    print("Test 2: Agent Tools (no LLM)")
    print("=" * 60)

    errors = []

    # initiate_task
    result = initiate_task("test task")
    if "Task initiated" in result:
        print(f"  ✓ initiate_task returns acknowledgement")
    else:
        errors.append(f"initiate_task returned unexpected: {result!r}")

    for prop in PROPERTIES:
        defn = get_property_definition(prop)
        if not defn or "Unknown property" in defn:
            errors.append(
                f"get_property_definition('{prop}') returned unexpected: {defn!r}"
            )
        else:
            print(f"  ✓ definition for '{prop}' ({len(defn)} chars)")

        examples = get_property_examples(prop)
        if not examples or "No examples" in examples:
            errors.append(
                f"get_property_examples('{prop}') returned unexpected: {examples!r}"
            )
        else:
            print(f"  ✓ examples for '{prop}' ({len(examples)} chars)")

    # Unknown property should return a graceful message
    unknown = get_property_definition("not_a_property")
    if "Unknown property" in unknown:
        print("  ✓ unknown property handled gracefully")
    else:
        errors.append(f"Expected graceful unknown-property message, got: {unknown!r}")

    if errors:
        for err in errors:
            print(f"  ✗ {err}")
        print(f"\n✗ Tool tests failed ({len(errors)} error(s))")
    else:
        print("\n✓ All tool tests passed")


# ---------------------------------------------------------------------------
# Test 3: Constraint checking (no LLM call)
# ---------------------------------------------------------------------------


def test_constraint_checking():
    """Verify that check_constraints detects the +O → +I violation."""
    print("\n" + "=" * 60)
    print("Test 3: Constraint Checking (no LLM)")
    print("=" * 60)

    errors = []

    # Should flag a violation: +O but identity=-I
    bad_ctx = json.dumps({"identity": "-I"})
    result = check_constraints("own_identity", "+O", context=bad_ctx)
    if "CONSTRAINT VIOLATION" in result:
        print("  ✓ Violation detected: +O with identity=-I")
    else:
        errors.append(f"Expected violation for +O/-I, got: {result!r}")

    # Should be clean: +O and identity=+I
    good_ctx = json.dumps({"identity": "+I"})
    result = check_constraints("own_identity", "+O", context=good_ctx)
    if "No violations detected" in result:
        print("  ✓ No violation: +O with identity=+I")
    else:
        errors.append(f"Expected no violation for +O/+I, got: {result!r}")

    # -O should never violate regardless of identity
    result = check_constraints("own_identity", "-O", context=bad_ctx)
    if "No violations detected" in result:
        print("  ✓ No violation: -O (constraint does not apply)")
    else:
        errors.append(f"Expected no violation for -O, got: {result!r}")

    # Properties without constraints should return cleanly
    result = check_constraints("rigidity", "+R")
    if "No specific constraints" in result or "No violations detected" in result:
        print("  ✓ Rigidity has no constraints (handled gracefully)")
    else:
        errors.append(f"Unexpected rigidity constraint result: {result!r}")

    if errors:
        for err in errors:
            print(f"  ✗ {err}")
        print(f"\n✗ Constraint tests failed ({len(errors)} error(s))")
    else:
        print("\n✓ All constraint tests passed")


# ---------------------------------------------------------------------------
# Test 4: Optimization (optional — makes many API calls)
# ---------------------------------------------------------------------------


def test_optimization():
    """Bootstrap few-shot optimize on a small labeled training set."""
    print("\n" + "=" * 60)
    print("Test 4: BootstrapFewShot Optimization")
    print("=" * 60)

    try:
        analyzer = DSPyAgentOntologyAnalyzer(model="gemini")

        training_examples = [
            analyzer.create_example(
                term="Student",
                description="A person enrolled in a university",
                rigidity="~R",
                identity="+I",
                own_identity="-O",
                unity="+U",
                dependence="+D",
                classification="Role",
            ),
            analyzer.create_example(
                term="Person",
                description="A human being",
                rigidity="+R",
                identity="+I",
                own_identity="+O",
                unity="+U",
                dependence="-D",
                classification="Natural Kind",
            ),
            analyzer.create_example(
                term="Red",
                description="The color red, as a property of objects",
                rigidity="-R",
                identity="-I",
                own_identity="-O",
                unity="-U",
                dependence="-D",
                classification="Attribution",
            ),
            analyzer.create_example(
                term="Employee",
                description="A person working for an organisation",
                rigidity="~R",
                identity="+I",
                own_identity="-O",
                unity="+U",
                dependence="+D",
                classification="Role",
            ),
            analyzer.create_example(
                term="Car",
                description="A four-wheeled motor vehicle",
                rigidity="+R",
                identity="+I",
                own_identity="+O",
                unity="+U",
                dependence="-D",
                classification="Artifact",
            ),
        ]

        print(
            f"\nTraining on {len(training_examples)} examples with BootstrapFewShot..."
        )

        analyzer.optimize(
            training_examples=training_examples,
            optimizer="BootstrapFewShot",
            max_bootstrapped_demos=2,
            max_labeled_demos=2,
            save_path="dspy_agent_optimized_model.json",
        )

        print("\nTesting optimized model on 'Teacher'...")
        result = analyzer.analyze(
            "Teacher", description="A person who teaches students in a school"
        )
        props = result["properties"]
        for prop in PROPERTIES:
            print(f"  {prop:15}: {props[prop]}")
        print(f"  Classification : {result['classification']}")

        print("\n✓ Optimization test completed")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DSPyAgentOntologyAnalyzer Test Suite")
    print("=" * 60)

    # Tool and constraint tests require no API calls
    test_agent_tools()
    test_constraint_checking()

    # Basic analysis — makes LLM calls
    print()
    test_basic_analysis()

    # Optimization — many LLM calls; uncomment to run
    # test_optimization()

    print("\n" + "=" * 60)
    print("Tests complete!")
    print("\nTo run the optimization test, uncomment test_optimization() above.")
    print("=" * 60)
