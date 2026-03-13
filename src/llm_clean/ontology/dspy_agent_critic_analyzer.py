"""
DSPy-based Agent+Critic Ontology Analyzer.

Extends DSPyAgentOntologyAnalyzer by adding a **critic** step after each
property agent.  If the critic rejects the agent's result, it provides
feedback and the agent reruns (up to ``max_critique_attempts`` times).

Architecture
------------
  Per-property ReAct agent  (same as DSPyAgentOntologyAnalyzer)
        ↓
  Per-property Critic        (DSPy Predict with CriticSignature)
        ↓  REJECT → feedback → agent reruns
        ↓  APPROVE → continue to next property

  ClassifySignature          → ChainOfThought (same as DSPyAgentOntologyAnalyzer)

  DSPyAgentCriticOntologyAnalysisModule – orchestrates everything
  DSPyAgentCriticOntologyAnalyzer       – public-facing class
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
        get_critic_system_prompt,
    )
    from .dspy_agent_analyzer import (
        AGENT_TOOLS,
        DSPyRigiditySignature,
        DSPyIdentitySignature,
        DSPyOwnIdentitySignature,
        DSPyUnitySignature,
        DSPyDependenceSignature,
        DSPyClassifySignature,
    )
except ImportError:
    from prompts import (
        AGENT_RIGIDITY_SYSTEM_PROMPT,
        AGENT_IDENTITY_SYSTEM_PROMPT,
        AGENT_OWN_IDENTITY_SYSTEM_PROMPT,
        AGENT_UNITY_SYSTEM_PROMPT,
        AGENT_DEPENDENCE_SYSTEM_PROMPT,
        get_critic_system_prompt,
    )
    from dspy_agent_analyzer import (
        AGENT_TOOLS,
        DSPyRigiditySignature,
        DSPyIdentitySignature,
        DSPyOwnIdentitySignature,
        DSPyUnitySignature,
        DSPyDependenceSignature,
        DSPyClassifySignature,
    )


# ---------------------------------------------------------------------------
# Critic DSPy Signatures
# ---------------------------------------------------------------------------


class DSPyCriticSignature(dspy.Signature):
    """Validate an ontological meta-property analysis.

    Review the proposed value and reasoning for a single OntoClean
    meta-property and decide whether to APPROVE or REJECT it.
    If rejecting, provide specific, actionable feedback.
    """

    property_name: str = dspy.InputField(
        desc="The meta-property being evaluated (e.g. 'rigidity', 'identity')"
    )
    term: str = dspy.InputField(desc="The entity/term that was analyzed")
    description: str = dspy.InputField(
        desc="Optional description of the entity", default=""
    )
    proposed_value: str = dspy.InputField(
        desc="The value proposed by the agent (e.g. '+R', '-I', '+O')"
    )
    proposed_reasoning: str = dspy.InputField(
        desc="The reasoning given by the agent for the proposed value"
    )

    status: str = dspy.OutputField(
        desc="'APPROVE' if the analysis is correct, 'REJECT' if it needs revision"
    )
    feedback: str = dspy.OutputField(
        desc="If REJECT: specific feedback on what is wrong and how to improve. "
        "If APPROVE: brief confirmation of why the analysis is correct."
    )


# ---------------------------------------------------------------------------
# Helper: run one property agent with a critic feedback loop
# ---------------------------------------------------------------------------


def _run_with_critique(
    agent,
    critic,
    property_name: str,
    value_attr: str,
    reasoning_attr: str,
    max_critique_attempts: int,
    **agent_kwargs,
) -> Dict[str, Any]:
    """
    Run *agent* then *critic* in a loop up to *max_critique_attempts* times.

    Returns a dict::

        {
            "value": "<property value>",
            "reasoning": "<reasoning text>",
            "critique_attempts": <int>,
            "critique_feedback": "<last feedback>",
            "approved": <bool>,
        }
    """
    last_feedback: Optional[str] = None

    for attempt in range(1, max_critique_attempts + 1):
        # Re-inject critic feedback into the agent on subsequent attempts
        kwargs = dict(agent_kwargs)
        if last_feedback is not None:
            # Append previous feedback to the description so the agent sees it
            existing_desc = kwargs.get("description", "")
            kwargs["description"] = (
                existing_desc
                + f"\n\n[Critic feedback from attempt {attempt - 1}]: {last_feedback}"
            )

        agent_result = agent(**kwargs)
        value = getattr(agent_result, value_attr, "")
        reasoning = getattr(agent_result, reasoning_attr, "")

        # Ask the critic
        critic_result = critic(
            property_name=property_name,
            term=kwargs.get("term", ""),
            description=agent_kwargs.get("description", ""),  # original description
            proposed_value=value,
            proposed_reasoning=reasoning,
        )

        status = (getattr(critic_result, "status", "") or "").strip().upper()
        feedback = getattr(critic_result, "feedback", "")

        if status == "APPROVE":
            return {
                "value": value,
                "reasoning": reasoning,
                "critique_attempts": attempt,
                "critique_feedback": feedback,
                "approved": True,
            }

        # REJECT — store feedback and loop
        last_feedback = feedback

    # Max attempts reached — return last result with a warning note
    return {
        "value": value,  # type: ignore[possibly-undefined]  # set in the loop
        "reasoning": reasoning,  # type: ignore[possibly-undefined]
        "critique_attempts": max_critique_attempts,
        "critique_feedback": f"Max critique attempts reached. Last feedback: {last_feedback}",
        "approved": False,
    }


# ---------------------------------------------------------------------------
# Module
# ---------------------------------------------------------------------------


class DSPyAgentCriticOntologyAnalysisModule(dspy.Module):
    """
    DSPy module where each meta-property ReAct agent is followed by a critic.

    If the critic rejects the agent's output, the agent reruns with feedback
    appended to the description.  This loop repeats up to ``max_critique_attempts``
    times per property.

    Evaluation order: Rigidity → Identity → Own Identity → Unity → Dependence → Classify.
    """

    def __init__(self, max_iters: int = 5, max_critique_attempts: int = 3):
        super().__init__()
        self.max_critique_attempts = max_critique_attempts

        # Property agents (same as DSPyAgentOntologyAnalysisModule)
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

        # Per-property critics
        self.rigidity_critic = dspy.Predict(DSPyCriticSignature)
        self.identity_critic = dspy.Predict(DSPyCriticSignature)
        self.own_identity_critic = dspy.Predict(DSPyCriticSignature)
        self.unity_critic = dspy.Predict(DSPyCriticSignature)
        self.dependence_critic = dspy.Predict(DSPyCriticSignature)

        # Final classifier
        self.classifier = dspy.ChainOfThought(DSPyClassifySignature)

    def forward(
        self, term: str, description: str = "", usage: str = ""
    ) -> dspy.Prediction:
        """
        Run all five property agents (each with a critic feedback loop) then classify.

        Returns a dspy.Prediction with fields:
            rigidity, identity, own_identity, unity, dependence,
            classification, reasoning,
            critique_info (dict of per-property attempt counts and feedback)
        """
        critique_info: Dict[str, Any] = {}

        # 1. Rigidity
        r_result = _run_with_critique(
            agent=self.rigidity_agent,
            critic=self.rigidity_critic,
            property_name="rigidity",
            value_attr="rigidity",
            reasoning_attr="rigidity_reasoning",
            max_critique_attempts=self.max_critique_attempts,
            term=term,
            description=description,
            usage=usage,
        )
        rigidity = r_result["value"]
        critique_info["rigidity_attempts"] = r_result["critique_attempts"]
        critique_info["rigidity_feedback"] = r_result["critique_feedback"]
        critique_info["rigidity_approved"] = r_result["approved"]

        # 2. Identity
        i_result = _run_with_critique(
            agent=self.identity_agent,
            critic=self.identity_critic,
            property_name="identity",
            value_attr="identity",
            reasoning_attr="identity_reasoning",
            max_critique_attempts=self.max_critique_attempts,
            term=term,
            description=description,
            usage=usage,
        )
        identity = i_result["value"]
        critique_info["identity_attempts"] = i_result["critique_attempts"]
        critique_info["identity_feedback"] = i_result["critique_feedback"]
        critique_info["identity_approved"] = i_result["approved"]

        # 3. Own Identity — passes identity result for constraint checking
        oi_result = _run_with_critique(
            agent=self.own_identity_agent,
            critic=self.own_identity_critic,
            property_name="own_identity",
            value_attr="own_identity",
            reasoning_attr="own_identity_reasoning",
            max_critique_attempts=self.max_critique_attempts,
            term=term,
            description=description,
            usage=usage,
            identity_result=identity,
        )
        own_identity = oi_result["value"]
        critique_info["own_identity_attempts"] = oi_result["critique_attempts"]
        critique_info["own_identity_feedback"] = oi_result["critique_feedback"]
        critique_info["own_identity_approved"] = oi_result["approved"]

        # 4. Unity
        u_result = _run_with_critique(
            agent=self.unity_agent,
            critic=self.unity_critic,
            property_name="unity",
            value_attr="unity",
            reasoning_attr="unity_reasoning",
            max_critique_attempts=self.max_critique_attempts,
            term=term,
            description=description,
            usage=usage,
        )
        unity = u_result["value"]
        critique_info["unity_attempts"] = u_result["critique_attempts"]
        critique_info["unity_feedback"] = u_result["critique_feedback"]
        critique_info["unity_approved"] = u_result["approved"]

        # 5. Dependence
        d_result = _run_with_critique(
            agent=self.dependence_agent,
            critic=self.dependence_critic,
            property_name="dependence",
            value_attr="dependence",
            reasoning_attr="dependence_reasoning",
            max_critique_attempts=self.max_critique_attempts,
            term=term,
            description=description,
            usage=usage,
        )
        dependence = d_result["value"]
        critique_info["dependence_attempts"] = d_result["critique_attempts"]
        critique_info["dependence_feedback"] = d_result["critique_feedback"]
        critique_info["dependence_approved"] = d_result["approved"]

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
            critique_info=critique_info,
        )


# ---------------------------------------------------------------------------
# Public analyzer class
# ---------------------------------------------------------------------------


class DSPyAgentCriticOntologyAnalyzer:
    """
    Agent+Critic ontology analyzer using DSPy.

    Each meta-property is first evaluated by a dedicated ReAct agent, then
    validated by a Predict-based critic.  If the critic rejects the result,
    the agent reruns with the critic's feedback appended, up to
    ``max_critique_attempts`` times per property.

    The public API is intentionally compatible with ``DSPyAgentOntologyAnalyzer``
    so the two can be used interchangeably, with the addition of
    ``critique_info`` in the returned dict.
    """

    # Same supported models as DSPyAgentOntologyAnalyzer
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
        max_critique_attempts: int = 3,
    ):
        """
        Initialize the DSPy agent+critic analyzer.

        Args:
            api_key: OpenRouter API key (optional, uses OPENROUTER_API_KEY env var).
            model: Model shortcut or full OpenRouter model name.  Same shortcuts
                   as DSPyAgentOntologyAnalyzer.
            optimized_module_path: Path to a saved optimized module (optional).
            train_file: Path to training data file (TSV, CSV, or JSON) (optional).
            test_file:  Path to test data file (TSV, CSV, or JSON) (optional).
            max_iters: Maximum ReAct iterations per agent (default: 5).
            max_critique_attempts: Maximum critique-and-retry cycles per property
                                   (default: 3).
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

        self.module = DSPyAgentCriticOntologyAnalysisModule(
            max_iters=max_iters,
            max_critique_attempts=max_critique_attempts,
        )

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
        Analyze an entity using per-property ReAct agents with critic validation.

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
                "reasoning": "...",
                "critique_info": {
                    "rigidity_attempts":       <int>,
                    "rigidity_feedback":       "...",
                    "rigidity_approved":       <bool>,
                    "identity_attempts":       <int>,
                    ...
                }
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
            "critique_info": result.critique_info,
        }

    # ------------------------------------------------------------------
    # Optimization (mirrors DSPyAgentOntologyAnalyzer.optimize)
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
        """Optimize the agent+critic module with a DSPy optimizer."""
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

        print(f"\n{optimizer} optimization complete!")
        return optimized_module

    # ------------------------------------------------------------------
    # Example helpers (mirrors DSPyAgentOntologyAnalyzer API)
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
    print("Initializing DSPy Agent+Critic Ontology Analyzer...")
    analyzer = DSPyAgentCriticOntologyAnalyzer(model="llama3b", max_critique_attempts=2)

    print("\nAnalyzing 'Student'...")
    result = analyzer.analyze(
        "Student", description="A person enrolled in a university"
    )

    print("\nResults:")
    print(json.dumps(result, indent=2))
