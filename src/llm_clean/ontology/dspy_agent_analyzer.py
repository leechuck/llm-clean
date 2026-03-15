"""
DSPy-based Agent Ontology Analyzer.

Each ontological meta-property (Rigidity, Identity, Own Identity, Unity,
Dependence) is evaluated by a dedicated DSPy ChainOfThought module, exactly
mirroring the per-property agent design in agent_analyzer.py but using DSPy
so the prompts can be optimized via BootstrapFewShot / MIPROv2.

Architecture
------------
  RigiditySignature     → dspy.ChainOfThought
  IdentitySignature     → dspy.ChainOfThought
  OwnIdentitySignature  → dspy.ChainOfThought  (receives identity result)
  UnitySignature        → dspy.ChainOfThought
  DependenceSignature   → dspy.ChainOfThought

  AgentOntologyAnalysisModule – orchestrates the five predictors and derives
                                classification deterministically from their
                                outputs (same rules as agent_analyzer.py).

  DSPyAgentOntologyAnalyzer   – public-facing class (compatible API with
                                DSPyOntologyAnalyzer and agent_analyzer.py).

Prompt source
-------------
Each signature's docstring is set directly from the corresponding
AGENT_*_SYSTEM_PROMPT constant in prompts.py so that the domain knowledge
lives in one place and DSPy optimizers can improve the instructions.
"""

import logging
import os
import json
import csv
import warnings
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
# Per-property DSPy Signatures
# ---------------------------------------------------------------------------
# Each docstring is populated from the matching AGENT_*_SYSTEM_PROMPT so that
# the instructions are defined once and can be tuned by DSPy optimizers.


class RigiditySignature(dspy.Signature):
    __doc__ = AGENT_RIGIDITY_SYSTEM_PROMPT

    term: str = dspy.InputField(desc="The entity/term to analyze")
    description: str = dspy.InputField(
        desc="Optional description of the entity", default=""
    )
    usage: str = dspy.InputField(desc="Optional usage context", default="")

    value: str = dspy.OutputField(
        desc="Rigidity value: '+R' (Rigid), '-R' (Non-Rigid), or '~R' (Anti-Rigid)"
    )
    reasoning: str = dspy.OutputField(
        desc="Explanation of why this entity has this rigidity value"
    )


class IdentitySignature(dspy.Signature):
    __doc__ = AGENT_IDENTITY_SYSTEM_PROMPT

    term: str = dspy.InputField(desc="The entity/term to analyze")
    description: str = dspy.InputField(
        desc="Optional description of the entity", default=""
    )
    usage: str = dspy.InputField(desc="Optional usage context", default="")

    value: str = dspy.OutputField(
        desc="Identity value: '+I' (carries identity condition) or '-I' (no identity condition)"
    )
    reasoning: str = dspy.OutputField(
        desc="Explanation of whether this entity carries an identity condition"
    )


class OwnIdentitySignature(dspy.Signature):
    __doc__ = AGENT_OWN_IDENTITY_SYSTEM_PROMPT

    term: str = dspy.InputField(desc="The entity/term to analyze")
    description: str = dspy.InputField(
        desc="Optional description of the entity", default=""
    )
    usage: str = dspy.InputField(desc="Optional usage context", default="")
    identity_value: str = dspy.InputField(
        desc="Previously determined Identity value ('+I' or '-I') — "
        "used to enforce the constraint: +O requires +I"
    )

    value: str = dspy.OutputField(
        desc="Own Identity value: '+O' (supplies own IC) or '-O' (does not supply own IC)"
    )
    reasoning: str = dspy.OutputField(
        desc="Explanation of whether this entity supplies its own identity condition"
    )


class UnitySignature(dspy.Signature):
    __doc__ = AGENT_UNITY_SYSTEM_PROMPT

    term: str = dspy.InputField(desc="The entity/term to analyze")
    description: str = dspy.InputField(
        desc="Optional description of the entity", default=""
    )
    usage: str = dspy.InputField(desc="Optional usage context", default="")

    value: str = dspy.OutputField(
        desc="Unity value: '+U' (Unifying), '-U' (Non-Unifying), or '~U' (Anti-Unity)"
    )
    reasoning: str = dspy.OutputField(
        desc="Explanation of the unity characteristics of this entity"
    )


class DependenceSignature(dspy.Signature):
    __doc__ = AGENT_DEPENDENCE_SYSTEM_PROMPT

    term: str = dspy.InputField(desc="The entity/term to analyze")
    description: str = dspy.InputField(
        desc="Optional description of the entity", default=""
    )
    usage: str = dspy.InputField(desc="Optional usage context", default="")

    value: str = dspy.OutputField(
        desc="Dependence value: '+D' (Dependent) or '-D' (Independent)"
    )
    reasoning: str = dspy.OutputField(
        desc="Explanation of the dependence characteristics of this entity"
    )


# ---------------------------------------------------------------------------
# Deterministic classification (mirrors agent_analyzer.py._classify_entity)
# ---------------------------------------------------------------------------


def _classify_entity(properties: Dict[str, str]) -> str:
    """
    Derive entity classification from meta-property values.

    Mirrors AgentOntologyAnalyzer._classify_entity exactly so that the DSPy
    and non-DSPy analyzers produce consistent classifications.
    """
    r = properties.get("rigidity")
    i = properties.get("identity")
    o = properties.get("own_identity")

    if r == "+R" and i == "+I" and o == "+O":
        return "Sortal (Rigid, supplies identity)"
    elif r == "+R" and i == "+I":
        return "Sortal (Rigid, carries identity)"
    elif r == "~R" and properties.get("dependence") == "+D":
        return "Role (Anti-rigid, dependent)"
    elif r == "~R":
        return "Role or Phase (Anti-rigid)"
    elif r == "-R" and i == "-I":
        return "Attribution (Non-rigid, no identity)"
    elif r == "-R":
        return "Category or Mixin (Non-rigid)"
    elif i == "-I":
        return "Attribution or Quality"
    else:
        return "Complex Type (see properties for details)"


# ---------------------------------------------------------------------------
# DSPy module
# ---------------------------------------------------------------------------


class AgentOntologyAnalysisModule(dspy.Module):
    """
    DSPy module that evaluates each meta-property with a dedicated
    ChainOfThought predictor, mirroring the per-agent design of
    AgentOntologyAnalyzer but with DSPy-optimizable prompts.

    Evaluation order: Rigidity → Identity → Own Identity → Unity → Dependence.
    Own Identity receives the Identity result to enforce +O → +I.
    Classification is derived deterministically (no extra LLM call).
    """

    def __init__(self):
        super().__init__()
        self.rigidity_agent = dspy.ChainOfThought(RigiditySignature)
        self.identity_agent = dspy.ChainOfThought(IdentitySignature)
        self.own_identity_agent = dspy.ChainOfThought(OwnIdentitySignature)
        self.unity_agent = dspy.ChainOfThought(UnitySignature)
        self.dependence_agent = dspy.ChainOfThought(DependenceSignature)

    def forward(
        self, term: str, description: str = "", usage: str = ""
    ) -> dspy.Prediction:
        """
        Run all five property predictors then derive classification.

        Each predictor call is wrapped in a try/except so that a parse
        failure from a weak model does not abort the entire analysis.
        A sentinel value ("N/A") is used for any property that fails;
        remaining predictors and the final classification still run.

        Returns a dspy.Prediction with fields:
            rigidity, rigidity_reasoning,
            identity, identity_reasoning,
            own_identity, own_identity_reasoning,
            unity, unity_reasoning,
            dependence, dependence_reasoning,
            classification
        """
        # 1. Rigidity
        try:
            r = self.rigidity_agent(term=term, description=description, usage=usage)
            rigidity = r.value
            rigidity_reasoning = r.reasoning
        except Exception as e:
            warnings.warn(f"Rigidity agent failed for '{term}': {e}")
            rigidity = "N/A"
            rigidity_reasoning = f"Agent failed: {e}"

        # 2. Identity
        try:
            i = self.identity_agent(term=term, description=description, usage=usage)
            identity = i.value
            identity_reasoning = i.reasoning
        except Exception as e:
            warnings.warn(f"Identity agent failed for '{term}': {e}")
            identity = "N/A"
            identity_reasoning = f"Agent failed: {e}"

        # 3. Own Identity — receives identity result for constraint enforcement
        try:
            oi = self.own_identity_agent(
                term=term,
                description=description,
                usage=usage,
                identity_value=identity,
            )
            own_identity = oi.value
            own_identity_reasoning = oi.reasoning
        except Exception as e:
            warnings.warn(f"Own-identity agent failed for '{term}': {e}")
            own_identity = "N/A"
            own_identity_reasoning = f"Agent failed: {e}"

        # 4. Unity
        try:
            u = self.unity_agent(term=term, description=description, usage=usage)
            unity = u.value
            unity_reasoning = u.reasoning
        except Exception as e:
            warnings.warn(f"Unity agent failed for '{term}': {e}")
            unity = "N/A"
            unity_reasoning = f"Agent failed: {e}"

        # 5. Dependence
        try:
            d = self.dependence_agent(term=term, description=description, usage=usage)
            dependence = d.value
            dependence_reasoning = d.reasoning
        except Exception as e:
            warnings.warn(f"Dependence agent failed for '{term}': {e}")
            dependence = "N/A"
            dependence_reasoning = f"Agent failed: {e}"

        # Deterministic classification (no extra LLM call)
        classification = _classify_entity(
            {
                "rigidity": rigidity,
                "identity": identity,
                "own_identity": own_identity,
                "unity": unity,
                "dependence": dependence,
            }
        )

        return dspy.Prediction(
            rigidity=rigidity,
            rigidity_reasoning=rigidity_reasoning,
            identity=identity,
            identity_reasoning=identity_reasoning,
            own_identity=own_identity,
            own_identity_reasoning=own_identity_reasoning,
            unity=unity,
            unity_reasoning=unity_reasoning,
            dependence=dependence,
            dependence_reasoning=dependence_reasoning,
            classification=classification,
        )


# ---------------------------------------------------------------------------
# Public analyzer class
# ---------------------------------------------------------------------------


class DSPyAgentOntologyAnalyzer:
    """
    Agent-based ontology analyzer using DSPy ChainOfThought per meta-property.

    Each property is evaluated by its own ChainOfThought predictor whose
    instructions come from the AGENT_*_SYSTEM_PROMPT constants in prompts.py.
    This mirrors AgentOntologyAnalyzer's design but makes the prompts
    optimizable via DSPy (BootstrapFewShot, MIPROv2, etc.).

    The public API is compatible with both DSPyOntologyAnalyzer and
    AgentOntologyAnalyzer so the three can be used interchangeably in
    batch scripts.
    """

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
        "mistral7b",
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
        "mistralai/mistral-7b-instruct",
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
        "mistral7b": "mistralai/mistral-7b-instruct",
        "qwen72b": "qwen/qwen-2.5-72b-instruct",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama3b",
        optimized_module_path: Optional[str] = None,
        train_file: Optional[str] = None,
        test_file: Optional[str] = None,
    ):
        """
        Initialize the DSPy agent-based analyzer.

        Args:
            api_key: OpenRouter API key (optional, uses OPENROUTER_API_KEY env var).
            model: Model shortcut or full OpenRouter model name. Shortcuts:
                   - "gemini"            -> google/gemini-3-flash-preview
                   - "anthropic"         -> anthropic/claude-4.5-sonnet
                   - "gemma9b"           -> google/gemma-2-9b-it
                   - "qwen7b"            -> qwen/qwen-2.5-7b-instruct
                   - "llama3b"           -> meta-llama/llama-3.2-3b-instruct
                   - "llama8b"           -> meta-llama/llama-3.1-8b-instruct
                   - "gpt4o-mini"        -> openai/gpt-4o-mini
                   - "llama70b"          -> meta-llama/llama-3.3-70b-instruct
                   - "mistral-small-3.1" -> mistralai/mistral-small-3.1-24b-instruct
                   - "mistral7b"         -> mistralai/mistral-7b-instruct
                   - "qwen72b"           -> qwen/qwen-2.5-72b-instruct
            optimized_module_path: Path to a saved optimized module (optional).
            train_file: Path to training data file (TSV, CSV, or JSON) (optional).
            test_file:  Path to test data file (TSV, CSV, or JSON) (optional).
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

        self.module = AgentOntologyAnalysisModule()

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
        Analyze an entity using per-property ChainOfThought agents.

        Returns:
            {
                "properties": {
                    "rigidity":     "+R" | "-R" | "~R",
                    "identity":     "+I" | "-I",
                    "own_identity": "+O" | "-O",
                    "unity":        "+U" | "-U" | "~U",
                    "dependence":   "+D" | "-D",
                },
                "reasoning": {
                    "rigidity":     "...",
                    "identity":     "...",
                    "own_identity": "...",
                    "unity":        "...",
                    "dependence":   "...",
                },
                "classification": "Sortal/Role/..."
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
            "reasoning": {
                "rigidity": result.rigidity_reasoning,
                "identity": result.identity_reasoning,
                "own_identity": result.own_identity_reasoning,
                "unity": result.unity_reasoning,
                "dependence": result.dependence_reasoning,
            },
            "classification": result.classification,
        }

    # ------------------------------------------------------------------
    # Optimization
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
    # Example helpers
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
