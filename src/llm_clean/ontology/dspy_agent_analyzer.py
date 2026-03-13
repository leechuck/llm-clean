"""
DSPy-based Agent Ontology Analyzer.

Each ontological meta-property (Rigidity, Identity, Own Identity, Unity, Dependence)
is evaluated by a dedicated DSPy ReAct agent.  The agents share access to a set of
ontology-definition tools so they can look up definitions and examples on demand,
then reason their way to a value.

The overall module orchestrates the five agents sequentially so that later agents
(e.g. own_identity) can receive the results of earlier ones as context.

Architecture
------------
  PropertyDefinitionTool  – returns the formal definition of any meta-property
  PropertyExamplesTool    – returns canonical positive/negative examples
  ConstraintCheckTool     – checks known OntoClean constraints (e.g. +O → +I)

  RigiditySignature       → ReAct agent
  IdentitySignature       → ReAct agent
  OwnIdentitySignature    → ReAct agent  (receives identity result for constraint)
  UnitySignature          → ReAct agent
  DependenceSignature     → ReAct agent

  ClassifySignature       → ChainOfThought  (derives classification from five values)

  AgentOntologyAnalysisModule  – orchestrates all of the above
  DSPyAgentOntologyAnalyzer    – public-facing class (mirrors DSPyOntologyAnalyzer API)
"""

import os
import json
import csv
import dspy
from typing import Optional, List, Dict, Any, Literal
from pathlib import Path
from dotenv import load_dotenv

# Try relative import first, fall back to direct import
try:
    from .prompts import (
        AGENT_RIGIDITY_SYSTEM_PROMPT,
        AGENT_IDENTITY_SYSTEM_PROMPT,
        AGENT_OWN_IDENTITY_SYSTEM_PROMPT,
        AGENT_UNITY_SYSTEM_PROMPT,
        AGENT_DEPENDENCE_SYSTEM_PROMPT,
    )
except ImportError:
    from prompts import (
        AGENT_RIGIDITY_SYSTEM_PROMPT,
        AGENT_IDENTITY_SYSTEM_PROMPT,
        AGENT_OWN_IDENTITY_SYSTEM_PROMPT,
        AGENT_UNITY_SYSTEM_PROMPT,
        AGENT_DEPENDENCE_SYSTEM_PROMPT,
    )


# ---------------------------------------------------------------------------
# Ontology knowledge base (used by agent tools)
# ---------------------------------------------------------------------------

_PROPERTY_DEFINITIONS = {
    "rigidity": (
        "Rigidity (R) describes whether a property is essential to all its instances:\n"
        "  +R (Rigid): The property is essential in ALL possible worlds. "
        "Every instance must always have this property.\n"
        "  -R (Non-Rigid): The property is not essential; instances can gain or lose it.\n"
        "  ~R (Anti-Rigid): The property is contingent BY DEFINITION — it is essential "
        "that it is NOT essential (e.g. roles, phases)."
    ),
    "identity": (
        "Identity (I) describes whether a property carries an Identity Condition (IC):\n"
        "  +I: The property carries an IC — there is a principled criterion to "
        "distinguish and re-identify instances over time.\n"
        "  -I: The property does NOT carry an IC — no such criterion exists."
    ),
    "own_identity": (
        "Own Identity (O) describes whether a property SUPPLIES its own global IC:\n"
        "  +O: The property supplies its own IC (does not inherit it).\n"
        "  -O: The property does not supply its own IC "
        "(inherits from a supertype, or has none).\n"
        "CONSTRAINT: +O implies +I — you cannot supply an IC without carrying one."
    ),
    "unity": (
        "Unity (U) describes whether instances are unified wholes:\n"
        "  +U (Unifying): Instances are intrinsic wholes with integrated parts.\n"
        "  -U (Non-Unifying): Instances are not necessarily wholes.\n"
        "  ~U (Anti-Unity): Instances are strictly aggregates or sums."
    ),
    "dependence": (
        "Dependence (D) describes existential dependence on other entities:\n"
        "  +D (Dependent): Instances necessarily depend on other specific entities.\n"
        "  -D (Independent): Instances can exist without depending on specific others."
    ),
}

_PROPERTY_EXAMPLES = {
    "rigidity": (
        "+R examples: Person, Physical Object, Number\n"
        "-R examples: Red Thing, Student (can stop being a student)\n"
        "~R examples: Role, Employee, Child (phase), Adult (phase)"
    ),
    "identity": (
        "+I examples: Person (DNA / fingerprints), Physical Object (spatio-temporal continuity)\n"
        "-I examples: Red, Amount of Matter, Property"
    ),
    "own_identity": (
        "+O examples: Person (supplies own IC), Physical Object (supplies own IC)\n"
        "-O examples: Student (inherits IC from Person), Red (has no IC to supply)"
    ),
    "unity": (
        "+U examples: Person (integrated biological system), Car (functional whole)\n"
        "-U examples: Red Thing, Amount of Water\n"
        "~U examples: Collection, Group, Forest"
    ),
    "dependence": (
        "+D examples: Student (depends on educational institution), "
        "Parasite (depends on host), Role (depends on relatum)\n"
        "-D examples: Person, Physical Object"
    ),
}

_CONSTRAINTS = {
    "own_identity": (
        "If own_identity = '+O', then identity MUST be '+I'.\n"
        "You cannot supply an identity condition without carrying one."
    ),
}


# ---------------------------------------------------------------------------
# Agent tools (plain callables — DSPy ReAct accepts any callable)
# ---------------------------------------------------------------------------


def get_property_definition(property_name: str) -> str:
    """Return the formal OntoClean definition for a meta-property.

    Args:
        property_name: One of 'rigidity', 'identity', 'own_identity', 'unity', 'dependence'.
    """
    key = property_name.lower().strip()
    return _PROPERTY_DEFINITIONS.get(
        key,
        f"Unknown property '{property_name}'. "
        f"Valid options: {list(_PROPERTY_DEFINITIONS.keys())}",
    )


def get_property_examples(property_name: str) -> str:
    """Return canonical positive and negative examples for a meta-property.

    Args:
        property_name: One of 'rigidity', 'identity', 'own_identity', 'unity', 'dependence'.
    """
    key = property_name.lower().strip()
    return _PROPERTY_EXAMPLES.get(
        key,
        f"No examples found for '{property_name}'.",
    )


def initiate_task(task_description: str = "") -> str:
    """Start a property analysis task. Call this first to acknowledge the task before using other tools.

    Args:
        task_description: Optional description of what you are about to analyze.
    """
    return "Task initiated. Use get_property_definition and get_property_examples to look up the property, then check_constraints if needed, and finish when ready."


def check_constraints(
    property_name: str, proposed_value: str, context: str = ""
) -> str:
    """Check OntoClean constraints for the given property and proposed value.

    Args:
        property_name: The property being evaluated.
        proposed_value: The proposed value (e.g. '+O', '-R').
        context: Optional JSON string of already-determined property values
                 (e.g. '{"identity": "+I"}').
    """
    key = property_name.lower().strip()
    constraint_info = _CONSTRAINTS.get(
        key, "No specific constraints for this property."
    )

    violations = []

    if key == "own_identity" and proposed_value == "+O":
        try:
            ctx = json.loads(context) if context else {}
        except json.JSONDecodeError:
            ctx = {}
        identity_val = ctx.get("identity", "unknown")
        if identity_val != "+I":
            violations.append(
                f"CONSTRAINT VIOLATION: '+O' requires identity='+I', "
                f"but identity='{identity_val}'. "
                f"Either change own_identity to '-O' or reconsider identity."
            )

    if violations:
        return (
            "Constraints:\n"
            + constraint_info
            + "\n\nViolations found:\n"
            + "\n".join(violations)
        )
    return "Constraints:\n" + constraint_info + "\n\nNo violations detected."


# Shared tool list for all agents
AGENT_TOOLS = [
    initiate_task,
    get_property_definition,
    get_property_examples,
    check_constraints,
]


# ---------------------------------------------------------------------------
# Per-property DSPy Signatures
# ---------------------------------------------------------------------------


class DSPyRigiditySignature(dspy.Signature):
    """Analyze the Rigidity meta-property of an ontological entity.

    Rigidity (R) describes whether a property is essential to all its instances
    in all possible worlds.  Use the available tools to look up the definition
    and examples, then determine the correct value: +R, -R, or ~R.
    """

    term: str = dspy.InputField(desc="The entity/term to analyze")
    description: str = dspy.InputField(
        desc="Optional description of the entity", default=""
    )
    usage: str = dspy.InputField(desc="Optional usage context", default="")

    rigidity: str = dspy.OutputField(
        desc="Rigidity value: '+R' (Rigid), '-R' (Non-Rigid), or '~R' (Anti-Rigid)"
    )
    rigidity_reasoning: str = dspy.OutputField(desc="Reasoning for the rigidity value")


class DSPyIdentitySignature(dspy.Signature):
    """Analyze the Identity meta-property of an ontological entity.

    Identity (I) describes whether the property carries an Identity Condition (IC).
    Use the available tools to look up the definition and examples, then determine
    the correct value: +I or -I.
    """

    term: str = dspy.InputField(desc="The entity/term to analyze")
    description: str = dspy.InputField(
        desc="Optional description of the entity", default=""
    )
    usage: str = dspy.InputField(desc="Optional usage context", default="")

    identity: str = dspy.OutputField(
        desc="Identity value: '+I' (carries identity condition) or '-I' (no identity condition)"
    )
    identity_reasoning: str = dspy.OutputField(desc="Reasoning for the identity value")


class DSPyOwnIdentitySignature(dspy.Signature):
    """Analyze the Own Identity meta-property of an ontological entity.

    Own Identity (O) describes whether the property supplies its OWN global identity
    condition.  Note the hard constraint: +O implies +I.  Use the check_constraints
    tool to verify your proposed value against the already-determined identity value.
    """

    term: str = dspy.InputField(desc="The entity/term to analyze")
    description: str = dspy.InputField(
        desc="Optional description of the entity", default=""
    )
    usage: str = dspy.InputField(desc="Optional usage context", default="")
    identity_result: str = dspy.InputField(
        desc="Previously determined identity value (e.g. '+I' or '-I') for constraint checking"
    )

    own_identity: str = dspy.OutputField(
        desc="Own Identity value: '+O' (supplies own IC) or '-O' (does not supply own IC)"
    )
    own_identity_reasoning: str = dspy.OutputField(
        desc="Reasoning for the own_identity value"
    )


class DSPyUnitySignature(dspy.Signature):
    """Analyze the Unity meta-property of an ontological entity.

    Unity (U) describes whether instances of the property are unified wholes.
    Use the available tools to look up the definition and examples, then determine
    the correct value: +U, -U, or ~U.
    """

    term: str = dspy.InputField(desc="The entity/term to analyze")
    description: str = dspy.InputField(
        desc="Optional description of the entity", default=""
    )
    usage: str = dspy.InputField(desc="Optional usage context", default="")

    unity: str = dspy.OutputField(
        desc="Unity value: '+U' (Unifying), '-U' (Non-Unifying), or '~U' (Anti-Unity)"
    )
    unity_reasoning: str = dspy.OutputField(desc="Reasoning for the unity value")


class DSPyDependenceSignature(dspy.Signature):
    """Analyze the Dependence meta-property of an ontological entity.

    Dependence (D) describes whether instances necessarily depend on other entities.
    Use the available tools to look up the definition and examples, then determine
    the correct value: +D or -D.
    """

    term: str = dspy.InputField(desc="The entity/term to analyze")
    description: str = dspy.InputField(
        desc="Optional description of the entity", default=""
    )
    usage: str = dspy.InputField(desc="Optional usage context", default="")

    dependence: str = dspy.OutputField(
        desc="Dependence value: '+D' (Dependent) or '-D' (Independent)"
    )
    dependence_reasoning: str = dspy.OutputField(
        desc="Reasoning for the dependence value"
    )


class DSPyClassifySignature(dspy.Signature):
    """Derive the OntoClean entity classification and overall reasoning from the five meta-property values."""

    term: str = dspy.InputField(desc="The entity/term")
    description: str = dspy.InputField(desc="Optional description", default="")
    rigidity: str = dspy.InputField(desc="Rigidity value (+R, -R, ~R)")
    identity: str = dspy.InputField(desc="Identity value (+I, -I)")
    own_identity: str = dspy.InputField(desc="Own Identity value (+O, -O)")
    unity: str = dspy.InputField(desc="Unity value (+U, -U, ~U)")
    dependence: str = dspy.InputField(desc="Dependence value (+D, -D)")

    classification: str = dspy.OutputField(
        desc="Entity classification (e.g. 'Sortal', 'Role', 'Mixin', 'Category', 'Phase Sortal')"
    )
    reasoning: str = dspy.OutputField(
        desc="Overall reasoning explaining the meta-property values and classification"
    )


# ---------------------------------------------------------------------------
# Agent module
# ---------------------------------------------------------------------------


class DSPyAgentOntologyAnalysisModule(dspy.Module):
    """
    DSPy module that evaluates each meta-property with a dedicated ReAct agent.

    Evaluation order: Rigidity → Identity → Own Identity → Unity → Dependence → Classify.
    Own Identity receives the Identity result so it can check the +O → +I constraint.
    """

    def __init__(self, max_iters: int = 5):
        super().__init__()
        self.rigidity_agent = dspy.ReAct(
            DSPyRigiditySignature, tools=AGENT_TOOLS, max_iters=max_iters
        )
        self.identity_agent = dspy.ReAct(
            DSPyIdentitySignature, tools=AGENT_TOOLS, max_iters=max_iters
        )
        self.own_identity_agent = dspy.ReAct(
            DSPyOwnIdentitySignature, tools=AGENT_TOOLS, max_iters=max_iters
        )
        self.unity_agent = dspy.ReAct(
            DSPyUnitySignature, tools=AGENT_TOOLS, max_iters=max_iters
        )
        self.dependence_agent = dspy.ReAct(
            DSPyDependenceSignature, tools=AGENT_TOOLS, max_iters=max_iters
        )
        self.classifier = dspy.ChainOfThought(DSPyClassifySignature)

    def forward(
        self, term: str, description: str = "", usage: str = ""
    ) -> dspy.Prediction:
        """
        Run all five property agents then derive the classification.

        Returns a dspy.Prediction with fields:
            rigidity, identity, own_identity, unity, dependence,
            classification, reasoning
        """
        # 1. Rigidity
        rigidity_result = self.rigidity_agent(
            term=term, description=description, usage=usage
        )
        rigidity = rigidity_result.rigidity

        # 2. Identity
        identity_result = self.identity_agent(
            term=term, description=description, usage=usage
        )
        identity = identity_result.identity

        # 3. Own Identity — passes identity result for constraint checking
        own_identity_result = self.own_identity_agent(
            term=term,
            description=description,
            usage=usage,
            identity_result=identity,
        )
        own_identity = own_identity_result.own_identity

        # 4. Unity
        unity_result = self.unity_agent(term=term, description=description, usage=usage)
        unity = unity_result.unity

        # 5. Dependence
        dependence_result = self.dependence_agent(
            term=term, description=description, usage=usage
        )
        dependence = dependence_result.dependence

        # 6. Classification
        classify_result = self.classifier(
            term=term,
            description=description,
            rigidity=rigidity,
            identity=identity,
            own_identity=own_identity,
            unity=unity,
            dependence=dependence,
        )

        return dspy.Prediction(
            rigidity=rigidity,
            identity=identity,
            own_identity=own_identity,
            unity=unity,
            dependence=dependence,
            classification=classify_result.classification,
            reasoning=classify_result.reasoning,
        )


# ---------------------------------------------------------------------------
# Public analyzer class
# ---------------------------------------------------------------------------


class DSPyAgentOntologyAnalyzer:
    """
    Agent-based ontology analyzer using DSPy.

    Each meta-property is evaluated by a dedicated ReAct agent that can call
    ontology-definition tools before committing to a value.  The interface is
    intentionally compatible with DSPyOntologyAnalyzer so the two can be used
    interchangeably in batch scripts.
    """

    # Supported models (same set as DSPyOntologyAnalyzer)
    SUPPORTED_MODELS = [
        # Shortcuts
        "gemini",
        "anthropic",
        "gemma9b",
        "qwen7b",
        "llama3b",
        "llama8b",
        "gpt4o-mini",
        "llama70b",
        "mistral-small-3.1",
        "qwen72b",
        # Full model names
        "google/gemini-3-flash-preview",
        "anthropic/claude-4.5-sonnet",
        "openai/gpt-4o-mini",
        "google/gemma-2-9b-it",
        "qwen/qwen-2.5-7b-instruct",
        "meta-llama/llama-3.2-3b-instruct",
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3.3-70b-instruct",
        "mistralai/mistral-small-3.1-24b-instruct",
        "qwen/qwen-2.5-72b-instruct",
    ]

    _MODEL_SHORTCUTS = {
        "anthropic": "anthropic/claude-4.5-sonnet",
        "gemini": "google/gemini-3-flash-preview",
        "gemma9b": "google/gemma-2-9b-it",
        "qwen7b": "qwen/qwen-2.5-7b-instruct",
        "llama3b": "meta-llama/llama-3.2-3b-instruct",
        "llama8b": "meta-llama/llama-3.1-8b-instruct",
        "gpt4o-mini": "openai/gpt-4o-mini",
        "llama70b": "meta-llama/llama-3.3-70b-instruct",
        "mistral-small-3.1": "mistralai/mistral-small-3.1-24b-instruct",
        "qwen72b": "qwen/qwen-2.5-72b-instruct",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama3b",
        optimized_module_path: Optional[str] = None,
        train_file: Optional[str] = None,
        test_file: Optional[str] = None,
        max_iters: int = 5,
    ):
        """
        Initialize the DSPy agent-based analyzer.

        Args:
            api_key: OpenRouter API key (optional, uses OPENROUTER_API_KEY env var).
            model: Model shortcut or full OpenRouter model name. Shortcuts:
                   - "gemini"          -> google/gemini-3-flash-preview
                   - "anthropic"       -> anthropic/claude-4.5-sonnet
                   - "gemma9b"         -> google/gemma-2-9b-it
                   - "qwen7b"          -> qwen/qwen-2.5-7b-instruct
                   - "llama3b"         -> meta-llama/llama-3.2-3b-instruct
                   - "llama8b"         -> meta-llama/llama-3.1-8b-instruct
                   - "gpt4o-mini"      -> openai/gpt-4o-mini
                   - "llama70b"        -> meta-llama/llama-3.3-70b-instruct
                   - "mistral-small-3.1" -> mistralai/mistral-small-3.1-24b-instruct
                   - "qwen72b"         -> qwen/qwen-2.5-72b-instruct
            optimized_module_path: Path to a saved optimized module (optional).
            train_file: Path to training data file (TSV, CSV, or JSON) (optional).
            test_file:  Path to test data file (TSV, CSV, or JSON) (optional).
            max_iters: Maximum ReAct iterations per agent (default: 5).
        """
        load_dotenv()

        model = self._MODEL_SHORTCUTS.get(model, model)
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError(
                "No API key found. Set OPENROUTER_API_KEY or pass api_key."
            )

        lm = dspy.LM(
            model=f"openrouter/{self.model}",
            api_key=self.api_key,
            api_base="https://openrouter.ai/api/v1",
        )
        dspy.configure(lm=lm)

        self.module = DSPyAgentOntologyAnalysisModule(max_iters=max_iters)

        if optimized_module_path and os.path.exists(optimized_module_path):
            print(f"Loading optimized module from {optimized_module_path}")
            self.module.load(optimized_module_path)

        self.train_examples: List[dspy.Example] = []
        self.test_examples: List[dspy.Example] = []

        if train_file:
            print(f"Loading training examples from {train_file}...")
            self.train_examples = self._load_examples_from_file(train_file)
            print(f"  Loaded {len(self.train_examples)} training examples")

        if test_file:
            print(f"Loading test examples from {test_file}...")
            self.test_examples = self._load_examples_from_file(test_file)
            print(f"  Loaded {len(self.test_examples)} test examples")

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyze(
        self,
        term: str,
        description: Optional[str] = None,
        usage: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze an entity using per-property ReAct agents.

        Returns:
            {
                "properties": {
                    "rigidity":     "+R" | "-R" | "~R",
                    "identity":     "+I" | "-I",
                    "own_identity": "+O" | "-O",
                    "unity":        "+U" | "-U" | "~U",
                    "dependence":   "+D" | "-D",
                },
                "classification": "Sortal/Role/...",
                "reasoning": "..."
            }
        """
        result = self.module(
            term=term,
            description=description or "",
            usage=usage or "",
        )
        return {
            "properties": {
                "rigidity": result.rigidity,
                "identity": result.identity,
                "own_identity": result.own_identity,
                "unity": result.unity,
                "dependence": result.dependence,
            },
            "classification": result.classification,
            "reasoning": result.reasoning,
        }

    # ------------------------------------------------------------------
    # Optimization (mirrors DSPyOntologyAnalyzer.optimize)
    # ------------------------------------------------------------------

    def optimize(
        self,
        training_examples: List[dspy.Example],
        validation_examples: Optional[List[dspy.Example]] = None,
        metric: Optional[callable] = None,
        optimizer: str = "BootstrapFewShot",
        save_path: Optional[str] = None,
        max_bootstrapped_demos: int = 3,
        max_labeled_demos: int = 3,
        num_candidate_programs: int = 4,
        num_threads: int = 16,
        breadth: int = 10,
        depth: int = 3,
        init_temperature: float = 1.0,
        auto: str = "medium",
    ):
        """
        Optimize the agent module with a DSPy optimizer.

        Accepts the same parameters as DSPyOntologyAnalyzer.optimize.
        """
        optimizer_map = {
            "bootstrapfewshot": "BootstrapFewShot",
            "bootstrapfewshotwithrandomsearch": "BootstrapFewShotWithRandomSearch",
            "copro": "COPRO",
            "miprov2": "MIPROv2",
        }
        optimizer_key = optimizer.lower().replace("_", "").replace("-", "")
        optimizer = optimizer_map.get(optimizer_key, optimizer)

        valid_optimizers = [
            "BootstrapFewShot",
            "BootstrapFewShotWithRandomSearch",
            "COPRO",
            "MIPROv2",
        ]
        if optimizer not in valid_optimizers:
            raise ValueError(
                f"Invalid optimizer '{optimizer}'. Must be one of {valid_optimizers}."
            )

        if metric is None:

            def default_metric(example, prediction, trace=None):
                pred = (
                    prediction
                    if isinstance(prediction, dict)
                    else {
                        "rigidity": getattr(prediction, "rigidity", None),
                        "identity": getattr(prediction, "identity", None),
                        "own_identity": getattr(prediction, "own_identity", None),
                        "unity": getattr(prediction, "unity", None),
                        "dependence": getattr(prediction, "dependence", None),
                    }
                )
                matches = sum(
                    [
                        pred.get("rigidity") == getattr(example, "rigidity", None),
                        pred.get("identity") == getattr(example, "identity", None),
                        pred.get("own_identity")
                        == getattr(example, "own_identity", None),
                        pred.get("unity") == getattr(example, "unity", None),
                        pred.get("dependence") == getattr(example, "dependence", None),
                    ]
                )
                return matches / 5.0

            metric = default_metric

        eval_examples = validation_examples or training_examples

        print(f"\nInitializing {optimizer} optimizer...")
        print(f"Training examples: {len(training_examples)}")
        print(f"Validation examples: {len(eval_examples)}")

        if optimizer == "BootstrapFewShot":
            from dspy.teleprompt import BootstrapFewShot

            teleprompter = BootstrapFewShot(
                metric=metric,
                max_bootstrapped_demos=max_bootstrapped_demos,
                max_labeled_demos=max_labeled_demos,
            )
        elif optimizer == "BootstrapFewShotWithRandomSearch":
            from dspy.teleprompt import BootstrapFewShotWithRandomSearch

            teleprompter = BootstrapFewShotWithRandomSearch(
                metric=metric,
                max_bootstrapped_demos=max_bootstrapped_demos,
                max_labeled_demos=max_labeled_demos,
                num_candidate_programs=num_candidate_programs,
                num_threads=num_threads,
            )
        elif optimizer == "COPRO":
            from dspy.teleprompt import COPRO

            teleprompter = COPRO(
                metric=metric,
                breadth=breadth,
                depth=depth,
                init_temperature=init_temperature,
            )
        else:  # MIPROv2
            from dspy.teleprompt import MIPROv2

            auto_mode: Literal["light", "medium", "heavy"] = auto  # type: ignore
            teleprompter = MIPROv2(
                metric=metric,
                auto=auto_mode,
                max_bootstrapped_demos=max_bootstrapped_demos,
                max_labeled_demos=max_labeled_demos,
            )

        print(f"\nStarting {optimizer} optimization...")
        print("This may take several minutes...\n")

        if optimizer == "COPRO":
            optimized_module = teleprompter.compile(
                self.module,
                trainset=training_examples,
                eval_kwargs={"num_threads": num_threads},
            )
        elif optimizer in ("BootstrapFewShot", "BootstrapFewShotWithRandomSearch"):
            optimized_module = teleprompter.compile(
                self.module,
                trainset=training_examples,
            )
        else:
            optimized_module = teleprompter.compile(
                self.module,
                trainset=training_examples,
                valset=eval_examples,
            )

        self.module = optimized_module

        if save_path:
            print(f"\nSaving optimized module to {save_path}")
            optimized_module.save(save_path)

        print(f"\n✓ {optimizer} optimization complete!")
        return optimized_module

    # ------------------------------------------------------------------
    # Example helpers (mirrors DSPyOntologyAnalyzer API)
    # ------------------------------------------------------------------

    @staticmethod
    def create_example(
        term: str,
        description: str = "",
        usage: str = "",
        rigidity: Optional[str] = None,
        identity: Optional[str] = None,
        own_identity: Optional[str] = None,
        unity: Optional[str] = None,
        dependence: Optional[str] = None,
        classification: Optional[str] = None,
        reasoning: Optional[str] = None,
    ) -> dspy.Example:
        """Create a training/validation example."""
        example_dict: Dict[str, Any] = {
            "term": term,
            "description": description,
            "usage": usage,
        }
        if rigidity is not None:
            example_dict["rigidity"] = rigidity
        if identity is not None:
            example_dict["identity"] = identity
        if own_identity is not None:
            example_dict["own_identity"] = own_identity
        if unity is not None:
            example_dict["unity"] = unity
        if dependence is not None:
            example_dict["dependence"] = dependence
        if classification is not None:
            example_dict["classification"] = classification
        if reasoning is not None:
            example_dict["reasoning"] = reasoning
        return dspy.Example(**example_dict).with_inputs("term", "description", "usage")

    def _load_examples_from_file(self, file_path: str) -> List[dspy.Example]:
        """Load dspy.Example objects from a TSV, CSV, or JSON file."""
        ext = Path(file_path).suffix.lower()
        examples = []

        if ext == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("JSON training file must contain a list of objects.")
            for item in data:
                examples.append(self._dict_to_example(item))

        elif ext in (".tsv", ".csv"):
            delimiter = "\t" if ext == ".tsv" else ","
            with open(file_path, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f, delimiter=delimiter):
                    examples.append(self._dict_to_example(row))
        else:
            raise ValueError(
                f"Unsupported file format '{ext}'. Supported: .json, .csv, .tsv"
            )

        return examples

    def _dict_to_example(self, data: Dict[str, Any]) -> dspy.Example:
        return self.create_example(
            term=data.get("term", ""),
            description=data.get("description", ""),
            usage=data.get("usage", ""),
            rigidity=data.get("rigidity"),
            identity=data.get("identity"),
            own_identity=data.get("own_identity"),
            unity=data.get("unity"),
            dependence=data.get("dependence"),
            classification=data.get("classification"),
            reasoning=data.get("reasoning"),
        )


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Initializing DSPy Agent Ontology Analyzer...")
    analyzer = DSPyAgentOntologyAnalyzer(model="llama3b")

    print("\nAnalyzing 'Student'...")
    result = analyzer.analyze(
        "Student", description="A person enrolled in a university"
    )

    print("\nResults:")
    print(json.dumps(result, indent=2))
