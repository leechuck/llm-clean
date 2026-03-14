#!/usr/bin/env python3
"""
Test script for DSPyAgentCriticOntologyAnalyzer.

Tests the agent+critic DSPy analyzer where each meta-property is evaluated
by a dedicated ChainOfThought predictor and then validated by a Predict-based
critic in a feedback loop.

Tests:
1. CriticSignature fields    – verify input/output fields (no LLM)
2. Critic loop (mock)        – _run_with_critique with mock agent/critic (no LLM)
3. critique_info structure   – verify analyze() returns well-formed critique_info (no LLM)
4. Constraint passing        – verify identity_value forwarded to own_identity_agent (no LLM)
5. Basic analysis            – run the full pipeline on a handful of terms (LLM)
6. Optimization              – BootstrapFewShot on a small training set (optional/LLM)
"""

import sys
import os

# Allow running directly from this directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dspy_agent_critic_analyzer import (
    DSPyAgentCriticOntologyAnalyzer,
    CriticSignature,
    AgentCriticOntologyAnalysisModule,
    _run_with_critique,
)
from dspy_agent_analyzer import _classify_entity

PROPERTIES = ["rigidity", "identity", "own_identity", "unity", "dependence"]

VALID_VALUES = {
    "rigidity": {"+R", "-R", "~R"},
    "identity": {"+I", "-I"},
    "own_identity": {"+O", "-O"},
    "unity": {"+U", "-U", "~U"},
    "dependence": {"+D", "-D"},
}


# ---------------------------------------------------------------------------
# Test 1: CriticSignature fields
# ---------------------------------------------------------------------------


def test_critic_signature():
    """Check that CriticSignature has the expected input/output fields."""
    print("=" * 60)
    print("Test 1: CriticSignature fields (no LLM)")
    print("=" * 60)

    errors = []

    input_fields = list(CriticSignature.input_fields.keys())
    output_fields = list(CriticSignature.output_fields.keys())

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
            print(f"  ✗ Missing InputField '{field}'")

    for field in expected_outputs:
        if field in output_fields:
            print(f"  ✓ OutputField '{field}' present")
        else:
            errors.append(f"Missing OutputField '{field}'")
            print(f"  ✗ Missing OutputField '{field}'")

    if errors:
        print(f"\n✗ Signature tests failed ({len(errors)} error(s))")
    else:
        print("\n✓ All signature field tests passed")

    assert not errors, "\n".join(errors)


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

    import dspy

    errors = []

    # --- Case A: critic approves on first attempt ---
    class FakeAgent:
        def __call__(self, **kwargs):
            return dspy.Prediction(value="+R", reasoning="It is always a person")

    class FakeCriticApprove:
        def __call__(self, **kwargs):
            return dspy.Prediction(status="APPROVE", feedback="Looks correct")

    result = _run_with_critique(
        agent=FakeAgent(),
        critic=FakeCriticApprove(),
        property_name="rigidity",
        max_critique_attempts=3,
        term="Person",
        description="A human being",
        usage="",
    )

    if result["value"] == "+R":
        print("  ✓ Correct value returned on first APPROVE")
    else:
        errors.append(f"Case A: expected '+R', got {result['value']!r}")
        print(f"  ✗ {errors[-1]}")

    if result["critique_attempts"] == 1:
        print("  ✓ Only 1 attempt needed for immediate APPROVE")
    else:
        errors.append(f"Case A: expected 1 attempt, got {result['critique_attempts']}")
        print(f"  ✗ {errors[-1]}")

    if result["approved"] is True:
        print("  ✓ approved=True when critic approves")
    else:
        errors.append("Case A: expected approved=True")
        print(f"  ✗ {errors[-1]}")

    # --- Case B: critic rejects once then approves ---
    call_count = [0]
    descriptions_received = []

    class FakeAgentB:
        def __call__(self, **kwargs):
            call_count[0] += 1
            descriptions_received.append(kwargs.get("description", ""))
            return dspy.Prediction(value="~R", reasoning="It is a role")

    critique_calls = [0]

    class FakeCriticRejectThenApprove:
        def __call__(self, **kwargs):
            critique_calls[0] += 1
            if critique_calls[0] == 1:
                return dspy.Prediction(
                    status="REJECT", feedback="Reconsider: Person is rigid"
                )
            return dspy.Prediction(status="APPROVE", feedback="Now correct")

    result2 = _run_with_critique(
        agent=FakeAgentB(),
        critic=FakeCriticRejectThenApprove(),
        property_name="rigidity",
        max_critique_attempts=3,
        term="Person",
        description="A human being",
        usage="",
    )

    if result2["critique_attempts"] == 2:
        print("  ✓ 2 attempts used when critic rejects then approves")
    else:
        errors.append(
            f"Case B: expected 2 attempts, got {result2['critique_attempts']}"
        )
        print(f"  ✗ {errors[-1]}")

    if result2["approved"] is True:
        print("  ✓ approved=True after eventual APPROVE")
    else:
        errors.append("Case B: expected approved=True after retry")
        print(f"  ✗ {errors[-1]}")

    if call_count[0] == 2:
        print("  ✓ Agent called twice (once per attempt)")
    else:
        errors.append(f"Case B: expected 2 agent calls, got {call_count[0]}")
        print(f"  ✗ {errors[-1]}")

    # Critic feedback should be injected into description on second call
    if (
        len(descriptions_received) >= 2
        and "Critic feedback" in descriptions_received[1]
    ):
        print("  ✓ Critic feedback injected into description on retry")
    else:
        errors.append(
            f"Case B: expected critic feedback in description on retry, "
            f"got: {descriptions_received[1] if len(descriptions_received) >= 2 else '(no second call)'!r}"
        )
        print(f"  ✗ {errors[-1]}")

    # --- Case C: critic always rejects — max attempts hit ---
    class FakeAgentC:
        def __call__(self, **kwargs):
            return dspy.Prediction(value="-R", reasoning="Not sure")

    class FakeCriticAlwaysReject:
        def __call__(self, **kwargs):
            return dspy.Prediction(status="REJECT", feedback="Still wrong")

    result3 = _run_with_critique(
        agent=FakeAgentC(),
        critic=FakeCriticAlwaysReject(),
        property_name="rigidity",
        max_critique_attempts=2,
        term="Person",
        description="A human being",
        usage="",
    )

    if result3["critique_attempts"] == 2:
        print("  ✓ Exactly max_critique_attempts used when always rejected")
    else:
        errors.append(
            f"Case C: expected 2 attempts (max), got {result3['critique_attempts']}"
        )
        print(f"  ✗ {errors[-1]}")

    if result3["approved"] is False:
        print("  ✓ approved=False when max attempts reached without approval")
    else:
        errors.append("Case C: expected approved=False at max attempts")
        print(f"  ✗ {errors[-1]}")

    if "Max critique attempts reached" in result3["critique_feedback"]:
        print("  ✓ critique_feedback indicates max attempts reached")
    else:
        errors.append(
            f"Case C: expected 'Max critique attempts reached' in feedback, "
            f"got: {result3['critique_feedback']!r}"
        )
        print(f"  ✗ {errors[-1]}")

    if errors:
        print(f"\n✗ Critic loop mock tests failed ({len(errors)} error(s))")
    else:
        print("\n✓ All critic loop mock tests passed")

    assert not errors, "\n".join(errors)


# ---------------------------------------------------------------------------
# Test 3: critique_info structure (mock module, no LLM)
# ---------------------------------------------------------------------------


def test_critique_info_structure():
    """
    Verify that analyze() returns a well-formed critique_info dict using a
    mocked module (no LLM).

    The expected shape is:
        critique_info = {
            "<prop>": {"attempts": int, "feedback": str, "approved": bool},
            ...
        }
    """
    print("\n" + "=" * 60)
    print("Test 3: critique_info structure (mock module, no LLM)")
    print("=" * 60)

    import dspy

    errors = []

    fake_critique_info = {
        prop: {
            "attempts": 1,
            "feedback": f"Looks good for {prop}",
            "approved": True,
        }
        for prop in PROPERTIES
    }
    # Simulate one rejection cycle on dependence
    fake_critique_info["dependence"] = {
        "attempts": 3,
        "feedback": "Max critique attempts reached. Last feedback: still uncertain",
        "approved": False,
    }

    fake_prediction = dspy.Prediction(
        rigidity="+R",
        rigidity_reasoning="Always a person",
        identity="+I",
        identity_reasoning="Has a unique ID",
        own_identity="+O",
        own_identity_reasoning="Supplies its own IC",
        unity="+U",
        unity_reasoning="Whole entity",
        dependence="-D",
        dependence_reasoning="Exists independently",
        classification="Sortal (Rigid, supplies identity)",
        critique_info=fake_critique_info,
    )

    class MockAnalyzer(DSPyAgentCriticOntologyAnalyzer):
        def __init__(self):
            # Skip LLM/API setup entirely
            self.module = lambda **kw: fake_prediction
            self.train_examples = []
            self.test_examples = []

    analyzer = MockAnalyzer()
    result = analyzer.analyze("Person", description="A human being")

    # Check top-level keys
    for key in ("properties", "reasoning", "classification", "critique_info"):
        if key in result:
            print(f"  ✓ Top-level key '{key}' present")
        else:
            errors.append(f"Missing top-level key '{key}'")
            print(f"  ✗ {errors[-1]}")

    ci = result.get("critique_info", {})

    for prop in PROPERTIES:
        if prop not in ci:
            errors.append(f"Missing property '{prop}' in critique_info")
            print(f"  ✗ Missing property '{prop}' in critique_info")
            continue
        entry = ci[prop]
        for subkey in ("attempts", "feedback", "approved"):
            if subkey in entry:
                print(f"  ✓ critique_info['{prop}']['{subkey}'] = {entry[subkey]!r}")
            else:
                errors.append(f"Missing subkey '{subkey}' in critique_info['{prop}']")
                print(f"  ✗ {errors[-1]}")

    # Verify reasoning is a dict, not a string
    reasoning = result.get("reasoning", {})
    if isinstance(reasoning, dict) and set(reasoning.keys()) == set(PROPERTIES):
        print("  ✓ reasoning is a dict with all five property keys")
    else:
        errors.append(
            f"Expected reasoning to be a dict with keys {PROPERTIES}, "
            f"got {type(reasoning).__name__}: {list(reasoning.keys()) if isinstance(reasoning, dict) else reasoning!r}"
        )
        print(f"  ✗ {errors[-1]}")

    if errors:
        print(f"\n✗ critique_info structure tests failed ({len(errors)} error(s))")
    else:
        print("\n✓ All critique_info structure tests passed")

    assert not errors, "\n".join(errors)


# ---------------------------------------------------------------------------
# Test 4: Constraint passing (no LLM)
# ---------------------------------------------------------------------------


def test_constraint_passing():
    """
    Verify that own_identity_agent receives the identity value determined by
    the identity agent, without making any LLM calls.
    """
    print("\n" + "=" * 60)
    print("Test 4: Constraint Passing (no LLM)")
    print("=" * 60)

    import dspy

    errors = []
    received_identity_values = []

    class FakePredictor:
        """Minimal stand-in for a dspy.ChainOfThought predictor."""

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

    class FakeCritic:
        def __call__(self, **kwargs):
            return dspy.Prediction(status="APPROVE", feedback="ok")

    module = AgentCriticOntologyAnalysisModule.__new__(
        AgentCriticOntologyAnalysisModule
    )
    module._compiled = False
    module.callbacks = []
    module.history = []
    module.max_critique_attempts = 1
    module.rigidity_agent = FakePredictor("+R", "rigidity")
    module.identity_agent = FakePredictor("+I", "identity")
    module.own_identity_agent = FakePredictor("+O", "own_identity")
    module.unity_agent = FakePredictor("+U", "unity")
    module.dependence_agent = FakePredictor("-D", "dependence")
    module.rigidity_critic = FakeCritic()
    module.identity_critic = FakeCritic()
    module.own_identity_critic = FakeCritic()
    module.unity_critic = FakeCritic()
    module.dependence_critic = FakeCritic()

    result = module(term="Person", description="A human being", usage="")

    if received_identity_values == ["+I"]:
        print("  ✓ identity_value '+I' forwarded to own_identity_agent")
    else:
        errors.append(
            f"own_identity_agent received identity_value={received_identity_values!r}, expected ['+I']"
        )
        print(f"  ✗ {errors[-1]}")

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
            print(f"  ✗ {errors[-1]}")

    # critique_info should be present and have all five properties
    ci = getattr(result, "critique_info", None)
    if isinstance(ci, dict) and set(ci.keys()) == set(PROPERTIES):
        print("  ✓ critique_info present with all five properties")
    else:
        errors.append(f"Expected critique_info dict with keys {PROPERTIES}, got {ci!r}")
        print(f"  ✗ {errors[-1]}")

    if errors:
        print(f"\n✗ Constraint tests failed ({len(errors)} error(s))")
    else:
        print("\n✓ All constraint tests passed")

    assert not errors, "\n".join(errors)


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
            reasons = result["reasoning"]
            ci = result.get("critique_info", {})

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

                # Print critique info per property
                if prop in ci:
                    entry = ci[prop]
                    print(
                        f"    critique : {entry.get('attempts')} attempt(s), "
                        f"approved={entry.get('approved')}"
                    )

            print(f"  Classification : {result['classification']}")

        print("\n✓ Basic analysis test completed")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()


# ---------------------------------------------------------------------------
# Test 6: Optimization (optional — many LLM calls)
# ---------------------------------------------------------------------------


def test_optimization():
    """Bootstrap few-shot optimize on a small labeled training set."""
    print("\n" + "=" * 60)
    print("Test 6: BootstrapFewShot Optimization (LLM)")
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
    test_critique_info_structure()
    test_constraint_passing()

    # Tests that make LLM calls
    print()
    test_basic_analysis()

    # Optimization — many LLM calls; uncomment to run
    # test_optimization()

    print("\n" + "=" * 60)
    print("Tests complete!")
    print("\nTo run the optimization test, uncomment test_optimization() above.")
    print("=" * 60)
