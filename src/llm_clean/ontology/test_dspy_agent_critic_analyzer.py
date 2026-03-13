#!/usr/bin/env python3
"""
Test script for DSPyAgentCriticOntologyAnalyzer.

Tests the agent+critic DSPy analyzer where each meta-property is evaluated
by a dedicated ReAct agent and then validated by a critic in a feedback loop.

Tests:
1. Critic signature       – verify DSPyCriticSignature fields exist
2. Critic loop (mock)     – _run_with_critique with a mock agent/critic (no LLM)
3. Agent tools            – call the standalone tool functions directly (no LLM)
4. Constraint checking    – verify the +O → +I constraint tool works correctly
5. Basic analysis         – run the full pipeline on a handful of terms (LLM)
6. Critique info          – verify critique_info is present and well-formed
7. Optimization           – BootstrapFewShot on a small training set (optional/LLM)
"""

import sys
import os
import json
from unittest.mock import MagicMock

# Allow running directly from this directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dspy_agent_critic_analyzer import (
    DSPyAgentCriticOntologyAnalyzer,
    DSPyCriticSignature,
    DSPyAgentCriticOntologyAnalysisModule,
    _run_with_critique,
)
from dspy_agent_analyzer import (
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
# Test 1: DSPyCriticSignature fields
# ---------------------------------------------------------------------------


def test_critic_signature():
    """Check that DSPyCriticSignature has the expected input/output fields."""
    print("=" * 60)
    print("Test 1: DSPyCriticSignature fields")
    print("=" * 60)

    errors = []
    import dspy

    sig = DSPyCriticSignature

    input_fields = list(sig.input_fields.keys())
    output_fields = list(sig.output_fields.keys())

    expected_inputs = [
        "property_name",
        "term",
        "description",
        "proposed_value",
        "proposed_reasoning",
    ]
    expected_outputs = ["status", "feedback"]

    for field in expected_inputs:
        if field in input_fields:
            print(f"  ✓ InputField  '{field}' present")
        else:
            errors.append(f"Missing InputField '{field}'")

    for field in expected_outputs:
        if field in output_fields:
            print(f"  ✓ OutputField '{field}' present")
        else:
            errors.append(f"Missing OutputField '{field}'")

    if errors:
        for err in errors:
            print(f"  ✗ {err}")
        print(f"\n✗ Signature tests failed ({len(errors)} error(s))")
    else:
        print("\n✓ All signature field tests passed")


# ---------------------------------------------------------------------------
# Test 2: _run_with_critique with mock agent/critic (no LLM)
# ---------------------------------------------------------------------------


def test_critic_loop_mock():
    """
    Verify the _run_with_critique helper using mock agent and critic.
    No LLM calls are made.
    """
    print("\n" + "=" * 60)
    print("Test 2: Critic feedback loop (mock, no LLM)")
    print("=" * 60)

    errors = []

    # --- Case A: critic approves on first attempt ---
    mock_agent = MagicMock()
    mock_agent.return_value = MagicMock(
        rigidity="+R", rigidity_reasoning="It is always a person"
    )

    mock_critic = MagicMock()
    mock_critic.return_value = MagicMock(status="APPROVE", feedback="Looks correct")

    result = _run_with_critique(
        agent=mock_agent,
        critic=mock_critic,
        property_name="rigidity",
        value_attr="rigidity",
        reasoning_attr="rigidity_reasoning",
        max_critique_attempts=3,
        term="Person",
        description="A human being",
        usage="",
    )

    if result["value"] == "+R":
        print("  ✓ Correct value returned on first APPROVE")
    else:
        errors.append(f"Expected '+R', got {result['value']!r}")

    if result["critique_attempts"] == 1:
        print("  ✓ Only 1 attempt needed for immediate APPROVE")
    else:
        errors.append(f"Expected 1 attempt, got {result['critique_attempts']}")

    if result["approved"] is True:
        print("  ✓ approved=True when critic approves")
    else:
        errors.append("Expected approved=True")

    if mock_agent.call_count == 1:
        print("  ✓ Agent called exactly once")
    else:
        errors.append(f"Expected 1 agent call, got {mock_agent.call_count}")

    # --- Case B: critic rejects once then approves ---
    mock_agent2 = MagicMock()
    mock_agent2.return_value = MagicMock(
        rigidity="~R", rigidity_reasoning="It is a role"
    )

    mock_critic2 = MagicMock()
    mock_critic2.side_effect = [
        MagicMock(status="REJECT", feedback="Reconsider: Person is rigid"),
        MagicMock(status="APPROVE", feedback="Now correct"),
    ]

    result2 = _run_with_critique(
        agent=mock_agent2,
        critic=mock_critic2,
        property_name="rigidity",
        value_attr="rigidity",
        reasoning_attr="rigidity_reasoning",
        max_critique_attempts=3,
        term="Person",
        description="A human being",
        usage="",
    )

    if result2["critique_attempts"] == 2:
        print("  ✓ 2 attempts used when critic rejects then approves")
    else:
        errors.append(f"Expected 2 attempts, got {result2['critique_attempts']}")

    if result2["approved"] is True:
        print("  ✓ approved=True after eventual APPROVE")
    else:
        errors.append("Expected approved=True after retry")

    if mock_agent2.call_count == 2:
        print("  ✓ Agent called twice (once per attempt)")
    else:
        errors.append(f"Expected 2 agent calls, got {mock_agent2.call_count}")

    # Check that feedback was injected into the description on the second call
    second_call_kwargs = mock_agent2.call_args_list[1][1]
    if "Critic feedback" in second_call_kwargs.get("description", ""):
        print("  ✓ Critic feedback injected into description on retry")
    else:
        errors.append(
            f"Expected critic feedback in description on retry, got: "
            f"{second_call_kwargs.get('description', '')!r}"
        )

    # --- Case C: critic always rejects — max attempts hit ---
    mock_agent3 = MagicMock()
    mock_agent3.return_value = MagicMock(rigidity="-R", rigidity_reasoning="Not sure")

    mock_critic3 = MagicMock()
    mock_critic3.return_value = MagicMock(status="REJECT", feedback="Still wrong")

    result3 = _run_with_critique(
        agent=mock_agent3,
        critic=mock_critic3,
        property_name="rigidity",
        value_attr="rigidity",
        reasoning_attr="rigidity_reasoning",
        max_critique_attempts=2,
        term="Person",
        description="A human being",
        usage="",
    )

    if result3["critique_attempts"] == 2:
        print("  ✓ Exactly max_critique_attempts used when always rejected")
    else:
        errors.append(f"Expected 2 attempts (max), got {result3['critique_attempts']}")

    if result3["approved"] is False:
        print("  ✓ approved=False when max attempts reached without approval")
    else:
        errors.append("Expected approved=False at max attempts")

    if "Max critique attempts reached" in result3["critique_feedback"]:
        print("  ✓ critique_feedback indicates max attempts reached")
    else:
        errors.append(
            f"Expected 'Max critique attempts reached' in feedback, got: "
            f"{result3['critique_feedback']!r}"
        )

    if errors:
        for err in errors:
            print(f"  ✗ {err}")
        print(f"\n✗ Critic loop mock tests failed ({len(errors)} error(s))")
    else:
        print("\n✓ All critic loop mock tests passed")


# ---------------------------------------------------------------------------
# Test 3: Agent tools (unit-level, no LLM call)
# ---------------------------------------------------------------------------


def test_agent_tools():
    """Call the ontology tool functions directly to verify they return content."""
    print("\n" + "=" * 60)
    print("Test 3: Agent Tools (no LLM)")
    print("=" * 60)

    errors = []

    result = initiate_task("test task")
    if "Task initiated" in result:
        print("  ✓ initiate_task returns acknowledgement")
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

    unknown = get_property_definition("not_a_property")
    if "Unknown property" in unknown:
        print("  ✓ Unknown property handled gracefully")
    else:
        errors.append(f"Expected graceful unknown-property message, got: {unknown!r}")

    if errors:
        for err in errors:
            print(f"  ✗ {err}")
        print(f"\n✗ Tool tests failed ({len(errors)} error(s))")
    else:
        print("\n✓ All tool tests passed")


# ---------------------------------------------------------------------------
# Test 4: Constraint checking (no LLM call)
# ---------------------------------------------------------------------------


def test_constraint_checking():
    """Verify that check_constraints detects the +O → +I violation."""
    print("\n" + "=" * 60)
    print("Test 4: Constraint Checking (no LLM)")
    print("=" * 60)

    errors = []

    bad_ctx = json.dumps({"identity": "-I"})
    result = check_constraints("own_identity", "+O", context=bad_ctx)
    if "CONSTRAINT VIOLATION" in result:
        print("  ✓ Violation detected: +O with identity=-I")
    else:
        errors.append(f"Expected violation for +O/-I, got: {result!r}")

    good_ctx = json.dumps({"identity": "+I"})
    result = check_constraints("own_identity", "+O", context=good_ctx)
    if "No violations detected" in result:
        print("  ✓ No violation: +O with identity=+I")
    else:
        errors.append(f"Expected no violation for +O/+I, got: {result!r}")

    result = check_constraints("own_identity", "-O", context=bad_ctx)
    if "No violations detected" in result:
        print("  ✓ No violation: -O (constraint does not apply)")
    else:
        errors.append(f"Expected no violation for -O, got: {result!r}")

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
# Test 5: Basic analysis (LLM calls)
# ---------------------------------------------------------------------------


def test_basic_analysis():
    """Run the full agent+critic pipeline on several well-known ontological entities."""
    print("\n" + "=" * 60)
    print("Test 5: Basic Analysis (LLM)")
    print("=" * 60)

    try:
        analyzer = DSPyAgentCriticOntologyAnalyzer(
            model="gemini", max_critique_attempts=2
        )

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

            # Test 6 inline: check critique_info
            ci = result.get("critique_info", {})
            if ci:
                print("  Critique info:")
                for prop in PROPERTIES:
                    attempts = ci.get(f"{prop}_attempts", "?")
                    approved = ci.get(f"{prop}_approved", "?")
                    print(f"    {prop:15}: {attempts} attempt(s), approved={approved}")
            else:
                print("  WARNING: critique_info missing from result")

        print("\n✓ Basic analysis test completed")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


# ---------------------------------------------------------------------------
# Test 6: critique_info structure (without LLM, using mock module)
# ---------------------------------------------------------------------------


def test_critique_info_structure():
    """
    Verify that the analyze() return dict contains a well-formed critique_info
    dict, using a mock module (no LLM).
    """
    print("\n" + "=" * 60)
    print("Test 6: critique_info structure (mock module, no LLM)")
    print("=" * 60)

    errors = []

    # Build a fake result that the module would return
    import dspy

    fake_prediction = dspy.Prediction(
        rigidity="+R",
        identity="+I",
        own_identity="+O",
        unity="+U",
        dependence="-D",
        classification="Sortal",
        reasoning="Test reasoning",
        critique_info={
            "rigidity_attempts": 1,
            "rigidity_feedback": "Good",
            "rigidity_approved": True,
            "identity_attempts": 2,
            "identity_feedback": "Revised after feedback",
            "identity_approved": True,
            "own_identity_attempts": 1,
            "own_identity_feedback": "Good",
            "own_identity_approved": True,
            "unity_attempts": 1,
            "unity_feedback": "Good",
            "unity_approved": True,
            "dependence_attempts": 3,
            "dependence_feedback": "Max critique attempts reached. Last feedback: ...",
            "dependence_approved": False,
        },
    )

    # Patch the module's forward call
    class _MockAnalyzer(DSPyAgentCriticOntologyAnalyzer):
        def __init__(self):
            # Skip LLM setup
            import dspy as _dspy

            self.module = MagicMock()
            self.module.return_value = fake_prediction
            self.train_examples = []
            self.test_examples = []

    analyzer = _MockAnalyzer()
    result = analyzer.analyze("Person", description="A human being")

    ci = result.get("critique_info")
    if ci is None:
        errors.append("critique_info key missing from analyze() result")
    else:
        print("  ✓ critique_info key present")

        for prop in PROPERTIES:
            for suffix in ("attempts", "feedback", "approved"):
                key = f"{prop}_{suffix}"
                if key in ci:
                    print(f"  ✓ critique_info['{key}'] = {ci[key]!r}")
                else:
                    errors.append(f"Missing key '{key}' in critique_info")

    if errors:
        for err in errors:
            print(f"  ✗ {err}")
        print(f"\n✗ critique_info structure tests failed ({len(errors)} error(s))")
    else:
        print("\n✓ All critique_info structure tests passed")


# ---------------------------------------------------------------------------
# Test 7: Optimization (optional — many LLM calls)
# ---------------------------------------------------------------------------


def test_optimization():
    """Bootstrap few-shot optimize on a small labeled training set."""
    print("\n" + "=" * 60)
    print("Test 7: BootstrapFewShot Optimization (LLM)")
    print("=" * 60)

    try:
        analyzer = DSPyAgentCriticOntologyAnalyzer(
            model="gemini", max_critique_attempts=2
        )

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
            save_path="dspy_agent_critic_optimized_model.json",
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
    print("DSPyAgentCriticOntologyAnalyzer Test Suite")
    print("=" * 60)

    # Tests that require no LLM calls
    test_critic_signature()
    test_critic_loop_mock()
    test_agent_tools()
    test_constraint_checking()
    test_critique_info_structure()

    # Tests that make LLM calls
    print()
    test_basic_analysis()

    # Optimization — many LLM calls; uncomment to run
    # test_optimization()

    print("\n" + "=" * 60)
    print("Tests complete!")
    print("\nTo run the optimization test, uncomment test_optimization() above.")
    print("=" * 60)
