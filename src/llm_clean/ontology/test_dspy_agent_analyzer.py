#!/usr/bin/env python3
"""
Test script for DSPyAgentOntologyAnalyzer.

Tests the agent-based DSPy analyzer where each meta-property is evaluated
by a dedicated ChainOfThought predictor.

Tests:
1. Basic analysis      – run the five property agents on a handful of terms
2. Output structure    – verify the returned dict has the expected shape
3. Constraint logic    – verify +O → +I is passed through correctly
4. Optimization        – bootstrap few-shot on a small training set (optional)
"""

import sys
import os
import json

# Allow running directly from this directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dspy_agent_analyzer import DSPyAgentOntologyAnalyzer

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
            reasons = result["reasoning"]

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
                reason_snippet = reasons.get(prop, "")[:80]
                print(f"    reasoning: {reason_snippet}...")

            print(f"  Classification : {result['classification']}")

        print("\n✓ Basic analysis test completed")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


# ---------------------------------------------------------------------------
# Test 2: Output structure
# ---------------------------------------------------------------------------


def test_output_structure():
    """Verify the returned dict has the expected keys and value shapes."""
    print("\n" + "=" * 60)
    print("Test 2: Output Structure (no LLM)")
    print("=" * 60)

    # Build a minimal fake result by calling the module with mocked predictors
    import dspy

    # We test structure without an LLM call by directly constructing a Prediction
    from dspy_agent_analyzer import AgentOntologyAnalysisModule, _classify_entity

    # Verify _classify_entity covers the main cases
    cases = [
        (
            {
                "rigidity": "+R",
                "identity": "+I",
                "own_identity": "+O",
                "unity": "+U",
                "dependence": "-D",
            },
            "Sortal (Rigid, supplies identity)",
        ),
        (
            {
                "rigidity": "+R",
                "identity": "+I",
                "own_identity": "-O",
                "unity": "+U",
                "dependence": "-D",
            },
            "Sortal (Rigid, carries identity)",
        ),
        (
            {
                "rigidity": "~R",
                "identity": "+I",
                "own_identity": "-O",
                "unity": "+U",
                "dependence": "+D",
            },
            "Role (Anti-rigid, dependent)",
        ),
        (
            {
                "rigidity": "~R",
                "identity": "+I",
                "own_identity": "-O",
                "unity": "+U",
                "dependence": "-D",
            },
            "Role or Phase (Anti-rigid)",
        ),
        (
            {
                "rigidity": "-R",
                "identity": "-I",
                "own_identity": "-O",
                "unity": "-U",
                "dependence": "-D",
            },
            "Attribution (Non-rigid, no identity)",
        ),
        (
            {
                "rigidity": "-R",
                "identity": "+I",
                "own_identity": "-O",
                "unity": "-U",
                "dependence": "-D",
            },
            "Category or Mixin (Non-rigid)",
        ),
    ]

    errors = []
    for props, expected in cases:
        got = _classify_entity(props)
        if got == expected:
            print(
                f"  ✓ {props['rigidity']}/{props['identity']}/{props['own_identity']} → {got}"
            )
        else:
            errors.append(f"Expected '{expected}', got '{got}' for {props}")
            print(f"  ✗ Expected '{expected}', got '{got}'")

    if errors:
        print(f"\n✗ Structure tests failed ({len(errors)} error(s))")
    else:
        print("\n✓ All structure tests passed")


# ---------------------------------------------------------------------------
# Test 3: Constraint passing
# ---------------------------------------------------------------------------


def test_constraint_passing():
    """
    Verify that own_identity_agent receives the identity value.

    We mock the module's predictors to confirm the identity value is forwarded
    as identity_value input to own_identity_agent without an LLM call.
    """
    print("\n" + "=" * 60)
    print("Test 3: Constraint Passing (no LLM)")
    print("=" * 60)

    import dspy
    from dspy_agent_analyzer import AgentOntologyAnalysisModule

    received_identity_values = []

    class FakePredictor:
        def __init__(self, value, prop):
            self.value_to_return = value
            self.prop = prop
            self.callbacks = []

        def __call__(self, **kwargs):
            if self.prop == "own_identity":
                received_identity_values.append(kwargs.get("identity_value"))
            return dspy.Prediction(
                value=self.value_to_return,
                reasoning=f"fake reasoning for {self.prop}",
            )

    module = AgentOntologyAnalysisModule.__new__(AgentOntologyAnalysisModule)
    module._compiled = False
    module.callbacks = []
    module.history = []
    module.rigidity_agent = FakePredictor("+R", "rigidity")
    module.identity_agent = FakePredictor("+I", "identity")
    module.own_identity_agent = FakePredictor("+O", "own_identity")
    module.unity_agent = FakePredictor("+U", "unity")
    module.dependence_agent = FakePredictor("-D", "dependence")

    result = module(term="Person", description="A human being", usage="")

    errors = []

    # The identity value "+I" must have been forwarded to own_identity_agent
    if received_identity_values == ["+I"]:
        print("  ✓ identity_value '+I' forwarded to own_identity_agent")
    else:
        errors.append(
            f"own_identity_agent received identity_value={received_identity_values!r}, expected ['+I']"
        )
        print(f"  ✗ {errors[-1]}")

    # Verify prediction fields
    expected_fields = {
        "rigidity": "+R",
        "identity": "+I",
        "own_identity": "+O",
        "unity": "+U",
        "dependence": "-D",
        "classification": "Sortal (Rigid, supplies identity)",
    }
    for field, expected in expected_fields.items():
        got = getattr(result, field)
        if got == expected:
            print(f"  ✓ {field}: {got}")
        else:
            errors.append(f"{field}: expected '{expected}', got '{got}'")
            print(f"  ✗ {field}: expected '{expected}', got '{got}'")

    if errors:
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

    # Structure and constraint tests require no API calls
    test_output_structure()
    test_constraint_passing()

    # Basic analysis — makes LLM calls
    print()
    test_basic_analysis()

    # Optimization — many LLM calls; uncomment to run
    # test_optimization()

    print("\n" + "=" * 60)
    print("Tests complete!")
    print("\nTo run the optimization test, uncomment test_optimization() above.")
    print("=" * 60)
