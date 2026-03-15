"""
DSPy-based Ontology Analyzer with Optimization.

This analyzer uses the DSPy framework to create an optimizable ontology analysis pipeline.
It uses an optimizer to improve the model.
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
    from .prompts import ANALYZER_SYSTEM_PROMPT
except ImportError:
    from prompts import ANALYZER_SYSTEM_PROMPT


class OntologyAnalysisSignature(dspy.Signature):
    """
    Signature for ontology analysis based on Guarino & Welty (2000) framework.

    This signature defines the input/output structure for the DSPy module.
    """

    # Instruction based on ANALYZER_SYSTEM_PROMPT
    __doc__ = ANALYZER_SYSTEM_PROMPT

    # Input fields
    term: str = dspy.InputField(desc="The entity/term to analyze")
    description: str = dspy.InputField(
        desc="Optional description of the entity", default=""
    )
    usage: str = dspy.InputField(
        desc="Optional usage context for the entity", default=""
    )

    # Output fields
    rigidity: str = dspy.OutputField(
        desc="Rigidity meta-property value: '+R' (Rigid), '-R' (Non-Rigid), or '~R' (Anti-Rigid)"
    )
    identity: str = dspy.OutputField(
        desc="Identity meta-property value: '+I' (carries identity) or '-I' (no identity)"
    )
    own_identity: str = dspy.OutputField(
        desc="Own Identity meta-property value: '+O' (supplies own IC) or '-O' (does not supply own IC)"
    )
    unity: str = dspy.OutputField(
        desc="Unity meta-property value: '+U' (Unifying), '-U' (Non-Unifying), or '~U' (Anti-Unity)"
    )
    dependence: str = dspy.OutputField(
        desc="Dependence meta-property value: '+D' (Dependent) or '-D' (Independent)"
    )
    classification: str = dspy.OutputField(
        desc="Entity classification based on meta-properties (e.g., 'Sortal', 'Role', 'Mixin')"
    )
    reasoning: str = dspy.OutputField(
        desc="Brief explanation of the analysis and classification"
    )


class OntologyAnalysisModule(dspy.Module):
    """
    DSPy module for ontology analysis.

    This module uses Chain-of-Thought reasoning to analyze entities
    according to the Guarino & Welty framework.
    """

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for better reasoning
        self.analyzer = dspy.ChainOfThought(OntologyAnalysisSignature)

    def forward(self, term: str, description: str = "", usage: str = ""):
        """
        Analyze an entity and return its ontological meta-properties.

        Args:
            term: The entity/term to analyze
            description: Optional description of the entity
            usage: Optional usage context

        Returns:
            dspy.Prediction with meta-properties and classification
        """
        result = self.analyzer(term=term, description=description, usage=usage)
        return result


class DSPyOntologyAnalyzer:
    """
    Ontology analyzer using DSPy with MIPROv2 optimization.

    This analyzer can be trained on examples to improve its performance
    using the MIPROv2 optimizer.
    """

    # Supported models for ontological analysis
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
        "mistralai/mistral-7b-instruct-v0.3",
        "qwen/qwen-2.5-72b-instruct",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama3b",
        optimized_module_path: Optional[str] = None,
        train_file: Optional[str] = None,
        test_file: Optional[str] = None,
    ):
        """
        Initialize the DSPy-based analyzer.

        Args:
            api_key: OpenRouter API key (optional, will use env variable if not provided)
            model: Model to use. Shortcuts available:
                   - "gemini" -> google/gemini-3-flash-preview (default)
                   - "anthropic" -> anthropic/claude-4.5-sonnet
                   - "gemma9b" -> google/gemma-2-9b-it
                   - "qwen7b" -> qwen/qwen-2.5-7b-instruct
                   - "llama3b" -> meta-llama/llama-3.2-3b-instruct
                   - "llama8b" -> meta-llama/llama-3.1-8b-instruct
                   - "gpt4o-mini" -> openai/gpt-4o-mini
                   - "llama70b" -> meta-llama/llama-3.3-70b-instruct
                   - "mistral-small-3.1" -> mistralai/mistral-small-3.1-24b-instruct
                   - "mistral7b" -> mistralai/mistral-7b-instruct-v0.3
                   - "qwen72b" -> qwen/qwen-2.5-72b-instruct
                   Or use full model names from OpenRouter.
            optimized_module_path: Path to a saved optimized module (optional)
            train_file: Path to training data file (TSV, CSV, or JSON) (optional)
            test_file: Path to test data file (TSV, CSV, or JSON) (optional)
        """
        # Load environment variables from .env file
        load_dotenv()

        # Set up default models for shortcuts
        model_shortcuts = {
            "anthropic": "anthropic/claude-4.5-sonnet",
            "gemini": "google/gemini-3-flash-preview",
            "gemma9b": "google/gemma-2-9b-it",
            "qwen7b": "qwen/qwen-2.5-7b-instruct",
            "llama3b": "meta-llama/llama-3.2-3b-instruct",
            "llama8b": "meta-llama/llama-3.1-8b-instruct",
            "gpt4o-mini": "openai/gpt-4o-mini",
            "llama70b": "meta-llama/llama-3.3-70b-instruct",
            "mistral-small-3.1": "mistralai/mistral-small-3.1-24b-instruct",
            "mistral7b": "mistralai/mistral-7b-instruct-v0.3",
            "qwen72b": "qwen/qwen-2.5-72b-instruct",
        }

        # Apply shortcut if available
        if model in model_shortcuts:
            model = model_shortcuts[model]

        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError("API key environment variable not set or not provided.")

        # Configure DSPy to use OpenRouter
        # DSPy uses LiteLLM under the hood, which supports OpenRouter
        lm = dspy.LM(
            model=f"openrouter/{self.model}",
            api_key=self.api_key,
            api_base="https://openrouter.ai/api/v1",
        )
        dspy.configure(lm=lm)

        # Initialize or load the module
        if optimized_module_path and os.path.exists(optimized_module_path):
            print(f"Loading optimized module from {optimized_module_path}")
            self.module = OntologyAnalysisModule()
            self.module.load(optimized_module_path)
        else:
            self.module = OntologyAnalysisModule()

        # Load training and test examples if files provided
        self.train_examples = []
        self.test_examples = []

        if train_file:
            print(f"Loading training examples from {train_file}...")
            self.train_examples = self._load_examples_from_file(train_file)
            print(f"  Loaded {len(self.train_examples)} training examples")

        if test_file:
            print(f"Loading test examples from {test_file}...")
            self.test_examples = self._load_examples_from_file(test_file)
            print(f"  Loaded {len(self.test_examples)} test examples")

    def _load_examples_from_file(self, file_path: str) -> List[dspy.Example]:
        """
        Load examples from a TSV, CSV, or JSON file.

        Args:
            file_path: Path to the data file

        Returns:
            List of dspy.Example objects
        """
        file_ext = Path(file_path).suffix.lower()
        examples = []

        if file_ext == ".json":
            # Load JSON file
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle list of dicts
            if isinstance(data, list):
                for item in data:
                    examples.append(self._create_example_from_dict(item))
            else:
                raise ValueError("JSON file must contain a list of objects")

        elif file_ext in [".tsv", ".csv"]:
            # Load TSV or CSV file
            delimiter = "\t" if file_ext == ".tsv" else ","

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    examples.append(self._create_example_from_dict(row))

        else:
            raise ValueError(
                f"Unsupported file format: {file_ext}. Supported: .tsv, .csv, .json"
            )

        return examples

    def _create_example_from_dict(self, data: Dict[str, Any]) -> dspy.Example:
        """
        Create a dspy.Example from a dictionary.

        Args:
            data: Dictionary with example data

        Returns:
            dspy.Example object
        """
        # Extract fields, with optional description, usage, classification, and reasoning
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

    def analyze(
        self, term: str, description: Optional[str] = None, usage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze an entity and return its ontological meta-properties.

        Args:
            term: The entity/term to analyze
            description: Optional description of the entity
            usage: Optional usage context

        Returns:
            Dictionary with structure:
            {
                "properties": {
                    "rigidity": "+R" | "-R" | "~R",
                    "identity": "+I" | "-I",
                    "own_identity": "+O" | "-O",
                    "unity": "+U" | "-U" | "~U",
                    "dependence": "+D" | "-D"
                },
                "classification": "Sortal/Role/etc",
                "reasoning": "Brief explanation."
            }
        """
        # Run the DSPy module
        result = self.module(
            term=term, description=description or "", usage=usage or ""
        )

        # Convert DSPy output to expected format
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

    def optimize(
        self,
        training_examples: List[dspy.Example],
        validation_examples: Optional[List[dspy.Example]] = None,
        metric: Optional[callable] = None,
        optimizer: str = "BootstrapFewShot",
        save_path: Optional[str] = None,
        # BootstrapFewShot parameters (default optimizer)
        max_bootstrapped_demos: int = 3,
        max_labeled_demos: int = 3,
        # BootstrapFewShotWithRandomSearch parameters
        num_candidate_programs: int = 10,
        num_threads: int = 4,
        # COPRO parameters
        breadth: int = 10,
        depth: int = 3,
        init_temperature: float = 1.0,
        # MIPROv2 parameters
        auto: str = "medium",
    ):
        """
        Optimize the analyzer using one of several DSPy optimizers.

        Args:
            training_examples: List of training examples (dspy.Example objects)
            validation_examples: Optional validation examples for evaluation
            metric: Metric function to optimize (if None, uses default accuracy metric)
            optimizer: Optimizer to use (default: 'BootstrapFewShot'). Case-insensitive.
                      Options: 'BootstrapFewShot', 'BootstrapFewShotWithRandomSearch', 'COPRO', 'MIPROv2'
                      Also accepts: 'bootstrap_few_shot', 'bootstrap-few-shot', 'mipro_v2', etc.
            save_path: Path to save the optimized module (optional)

            # BootstrapFewShot parameters (default: good for 20 samples)
            max_bootstrapped_demos: Max bootstrapped demonstrations (default: 3)
            max_labeled_demos: Max labeled demonstrations (default: 3)

            # BootstrapFewShotWithRandomSearch parameters (default: good for 20 samples)
            num_candidate_programs: Number of candidate programs to generate (default: 10)
            num_threads: Number of parallel threads (default: 4)

            # COPRO parameters (default: good for 20 samples)
            breadth: Number of instructions to generate per step (default: 10)
            depth: Number of optimization rounds (default: 3)
            init_temperature: Initial temperature for generation (default: 1.0)

            # MIPROv2 parameters (default: good for 20 samples)
            auto: Optimization mode - 'light', 'medium', 'heavy' (default: 'medium')

        Returns:
            Optimized module

        Recommended optimizers for small datasets (20 samples):
            - BootstrapFewShot (default): Fast, simple, effective for small datasets
            - BootstrapFewShotWithRandomSearch: More thorough, tests multiple prompt variations
            - COPRO: Good for instruction optimization, moderate speed
            - MIPROv2: Most advanced, but may be overkill for 20 samples
        """
        # Normalize optimizer to proper case (case-insensitive matching)
        optimizer_map = {
            "bootstrapfewshot": "BootstrapFewShot",
            "bootstrapfewshotwithrandomsearch": "BootstrapFewShotWithRandomSearch",
            "copro": "COPRO",
            "miprov2": "MIPROv2",
        }

        optimizer_lower = optimizer.lower().replace("_", "").replace("-", "")
        if optimizer_lower in optimizer_map:
            optimizer = optimizer_map[optimizer_lower]

        # Validate optimizer choice
        valid_optimizers = [
            "BootstrapFewShot",
            "BootstrapFewShotWithRandomSearch",
            "COPRO",
            "MIPROv2",
        ]
        if optimizer not in valid_optimizers:
            raise ValueError(
                f"Invalid optimizer: {optimizer}. Must be one of {valid_optimizers} (case-insensitive)"
            )

        if metric is None:
            # Default metric: check if all properties match
            def default_metric(example, prediction, trace=None):
                # Convert prediction to dict if it's a Prediction object
                if hasattr(prediction, "__dict__"):
                    pred_dict = {
                        "rigidity": prediction.rigidity,
                        "identity": prediction.identity,
                        "own_identity": prediction.own_identity,
                        "unity": prediction.unity,
                        "dependence": prediction.dependence,
                    }
                else:
                    pred_dict = prediction

                # Check if all properties match
                matches = sum(
                    [
                        pred_dict.get("rigidity") == example.rigidity,
                        pred_dict.get("identity") == example.identity,
                        pred_dict.get("own_identity") == example.own_identity,
                        pred_dict.get("unity") == example.unity,
                        pred_dict.get("dependence") == example.dependence,
                    ]
                )
                # Return proportion of correct properties (0.0 to 1.0)
                return matches / 5.0

            metric = default_metric

        # Use validation examples if provided, otherwise use training examples
        eval_examples = (
            validation_examples if validation_examples else training_examples
        )

        # Initialize the appropriate optimizer
        print(f"\nInitializing {optimizer} optimizer...")
        print(f"Training examples: {len(training_examples)}")
        print(f"Validation examples: {len(eval_examples)}")

        if optimizer == "BootstrapFewShot":
            from dspy.teleprompt import BootstrapFewShot

            print(
                f"Parameters: max_bootstrapped_demos={max_bootstrapped_demos}, max_labeled_demos={max_labeled_demos}"
            )
            teleprompter = BootstrapFewShot(
                metric=metric,
                max_bootstrapped_demos=max_bootstrapped_demos,
                max_labeled_demos=max_labeled_demos,
            )

        elif optimizer == "BootstrapFewShotWithRandomSearch":
            from dspy.teleprompt import BootstrapFewShotWithRandomSearch

            print(
                f"Parameters: num_candidate_programs={num_candidate_programs}, num_threads={num_threads}"
            )
            teleprompter = BootstrapFewShotWithRandomSearch(
                metric=metric,
                max_bootstrapped_demos=max_bootstrapped_demos,
                max_labeled_demos=max_labeled_demos,
                num_candidate_programs=num_candidate_programs,
                num_threads=num_threads,
            )

        elif optimizer == "COPRO":
            from dspy.teleprompt import COPRO

            print(
                f"Parameters: breadth={breadth}, depth={depth}, init_temperature={init_temperature}"
            )
            teleprompter = COPRO(
                metric=metric,
                breadth=breadth,
                depth=depth,
                init_temperature=init_temperature,
            )

        elif optimizer == "MIPROv2":
            from dspy.teleprompt import MIPROv2

            print(
                f"Parameters: auto={auto}, max_bootstrapped_demos={max_bootstrapped_demos}, max_labeled_demos={max_labeled_demos}"
            )
            # Cast auto to Literal type for MIPROv2
            auto_mode: Literal["light", "medium", "heavy"] = auto  # type: ignore
            teleprompter = MIPROv2(
                metric=metric,
                auto=auto_mode,
                max_bootstrapped_demos=max_bootstrapped_demos,
                max_labeled_demos=max_labeled_demos,
            )
        else:
            raise ValueError(f"Unknown optimizer: {optimizer}")

        # Compile (optimize) the module
        print(f"\nStarting {optimizer} optimization...")
        print("This may take several minutes...\n")

        # Different optimizers use different compile signatures
        if optimizer == "COPRO":
            # COPRO requires eval_kwargs (passed to the metric function)
            optimized_module = teleprompter.compile(
                self.module,
                trainset=training_examples,
                eval_kwargs={"num_threads": num_threads},
            )
        elif optimizer in [
            "BootstrapFewShot",
            "BootstrapFewShotWithRandomSearch",
        ]:
            # These optimizers don't use valset parameter
            optimized_module = teleprompter.compile(
                self.module,
                trainset=training_examples,
            )
        else:
            # MIPROv2 supports valset
            optimized_module = teleprompter.compile(
                self.module,
                trainset=training_examples,
                valset=eval_examples,
            )

        # Update the module
        self.module = optimized_module

        # Save if path provided
        if save_path:
            print(f"\nSaving optimized module to {save_path}")
            optimized_module.save(save_path)

        print(f"\n✓ {optimizer} optimization complete!")
        return optimized_module

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
        """
        Create a training/validation example for optimization.

        Args:
            term: The entity/term
            description: Optional description
            usage: Optional usage context
            rigidity: Expected rigidity value
            identity: Expected identity value
            own_identity: Expected own_identity value
            unity: Expected unity value
            dependence: Expected dependence value
            classification: Expected classification
            reasoning: Expected reasoning

        Returns:
            dspy.Example object
        """
        example_dict = {
            "term": term,
            "description": description,
            "usage": usage,
        }

        # Add labeled outputs if provided
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


if __name__ == "__main__":
    # Example usage
    print("Initializing DSPy Ontology Analyzer...")
    analyzer = DSPyOntologyAnalyzer(model="llama3b")

    print("\nAnalyzing 'Student'...")
    result = analyzer.analyze(
        "Student", description="A person enrolled in a university"
    )

    print("\nResults:")
    print(json.dumps(result, indent=2))

    print("\n" + "=" * 60)
    print("To optimize the analyzer, create training examples and call:")
    print("  examples = [")
    print("    analyzer.create_example(")
    print("      term='Student',")
    print("      description='A person enrolled in a university',")
    print("      rigidity='~R',")
    print("      identity='+I',")
    print("      own_identity='-O',")
    print("      unity='+U',")
    print("      dependence='+D',")
    print("      classification='Role'")
    print("    ),")
    print("    # ... more examples ...")
    print("  ]")
    print(
        "  analyzer.optimize(training_examples=examples, save_path='optimized_model')"
    )
    print("=" * 60)
