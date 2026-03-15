# LLM-Clean: Ontologically Sound Taxonomy Generation

LLM-Clean is a framework for generating and validating taxonomies using Large Language Models (LLMs) guided by the **OntoClean** methodology (Guarino & Welty, 2000). It supports zero-shot generation and advanced agentic workflows with automated critique.

This repository accompanies the research:  
*`LLM-Clean: Ontologically Sound Taxonomy Generation with Agentic Critique`*

---

## 📂 Project Structure

The project is organized into a modular library and script-based entry points:

- **`src/llm_clean/`**: Core package logic.
  - `agents/`: Agentic workflows (Taxonomist & Critic interaction).
  - `ontology/`: OntoClean property analysis and violation detection.
  - `utils/`: Shared utilities for LLM interaction (OpenRouter).
- **`scripts/`**: Executable CLI tools and benchmark runners.
- **`data/`**: Input datasets and raw academic resources.
- **`output/`**: Generated taxonomies, OWL files, and analysis results.
- **`docs/reports/`**: Detailed benchmark reports for multiple models.

---

## 🚀 Getting Started

### Prerequisites
- [uv](https://github.com/astral-sh/uv) (recommended) or Python 3.10+
- [Docker](https://www.docker.com/) (optional, for containerized execution)
- OpenRouter API Key (in a `.env` file)

### Installation
```bash
# Clone and install dependencies
git clone https://github.com/leechuck/llm-clean.git
cd llm-clean
uv pip install -e .
```

### Reproduce Results
Run the master reproduction script to download resources, generate the messy taxonomy, and (optionally) run benchmarks:
```bash
chmod +x reproduce.sh
./reproduce.sh
```

### Reproduce Batch Analysis Experiments
Run comprehensive batch analysis experiments comparing different models and background file configurations:
```bash
chmod +x reproduce_batch_analysis.sh
./reproduce_batch_analysis.sh
```

**What this script does:**

1. **Standard Mode Analysis** (both Claude and Gemini):
   - No background files (hardcoded prompts only)
   - PDF background file (Guarino & Welty paper)
   - Converted text background file
   - Corrected text background file
   - 8 total analysis runs

2. **Agentic Mode Analysis** (both Claude and Gemini):
   - No background files
   - Simple property-specific sections (no introduction)
   - Augmented sections (with introduction context)
   - 6 total analysis runs

3. **Agentic Mode with Critic Validation** (both Claude and Gemini):
   - No background files
   - Simple property-specific sections (no introduction)
   - Augmented sections (with introduction context)
   - 6 total analysis runs with `--max-critique-attempts 3`
   - Each property analysis validated by critic with feedback loop

4. **Evaluation**: Compares all analysis results (20 total runs) against ground truth data
   - Standard accuracy evaluation using `evaluate_analysis.py`
   - Classification metrics evaluation using `evaluate_classification_metrics.py`

5. **Classification Metrics Generation** (20 evaluations):
   - Generates detailed precision, recall, F1-score, and confusion matrix metrics
   - Creates CSV files for each analysis run in `output/evaluation_results/classify_*.csv`
   - Includes per-class, macro-averaged, and overall metrics

6. **Aggregation**: Collects all evaluations into summary reports:
   - `output/collect_non_agent_results.tsv` / `.md`
   - `output/collect_agent_results.tsv` / `.md`
   - `output/collect_agent_critic_results.tsv` / `.md`
   - `docs/reports/NON_AGENT_BATCH_ANALYSIS_REPORT.md`
   - `docs/reports/AGENT_BATCH_ANALYSIS_REPORT.md`
   - `docs/reports/AGENT_CRITIC_BATCH_ANALYSIS_REPORT.md`

**Requirements:**
- `.env` file with API keys (ANTHROPIC_API_KEY, GEMINI_API_KEY or GOOGLE_API_KEY)
- Ground truth data at `data/raw/ground_truth.tsv`
- Guarino paper resources in `data/raw/`

### Using Make for Granular Control

For more control over the reproduction process, use the provided Makefile:

```bash
# See all available targets
make help

# Run complete reproduction pipeline
make all

# Run only specific steps
make reproduce-static          # Static reproduction only
make batch-non-agent-claude    # Only Claude non-agent analysis
make batch-agent               # All agent analyses (both models)
make batch-critic              # All critic analyses (both models)

# Run evaluation and reports for specific mode
make eval-agent collect-agent  # Evaluate and collect agent results

# Generate classification metrics for specific mode
make classify-non-agent        # Classification metrics for non-agent analyses
make classify-agent            # Classification metrics for agent analyses
make classify-critic           # Classification metrics for critic analyses

# Run complete batch analysis (20 experiments + 20 classification evaluations)
make reproduce-batch

# Clean outputs
make clean
```

**Makefile Target Categories:**

- **Setup**: `setup`, `directories`, `clean`
- **Static Reproduction**: `reproduce-static`, `download-paper`, `generate-owl`
- **Benchmarks**: `benchmark-zeroshot`, `benchmark-agentic`
- **Batch Analysis**: `batch-non-agent`, `batch-agent`, `batch-critic` (+ model-specific variants)
- **Evaluation**: `eval-non-agent`, `eval-agent`, `eval-critic` (+ model-specific variants)
- **Classification Metrics**: `classify-non-agent`, `classify-agent`, `classify-critic` (+ model-specific variants)
- **Reports**: `collect-non-agent`, `collect-agent`, `collect-critic`, `reports`
- **Generate DSPy Models**: `generate-large-llm-dspy-models`, `generate-small-llm-dspy-models` (+ per-model and per-optimizer variants)
- **Generate DSPy Agent Models**: `generate-large-llm-dspy-agent-models`, `generate-small-llm-dspy-agent-models` (+ per-model and per-optimizer variants)
- **Generate DSPy Agent+Critic Models**: `generate-large-llm-dspy-agent-critic-models`, `generate-small-llm-dspy-agent-critic-models` (+ per-model and per-optimizer variants)
- **Batch DSPy Agent Analysis**: `batch-agent-dspy-small-models`, `batch-agent-dspy-anthropic-small-models`, `batch-agent-dspy-gemini-small-models` (+ per-combination variants)
- **Batch DSPy Agent+Critic Analysis**: `batch-agent-critic-dspy-small-models`, `batch-agent-critic-dspy-anthropic-small-models`, `batch-agent-critic-dspy-gemini-small-models` (+ per-combination variants)
- **Complete Workflows**: `all`, `reproduce-batch`

Run `make help` to see the full list with descriptions.

## 🧪 OntoClean Property Analysis

LLM-Clean provides multiple modes for analyzing entity meta-properties (Rigidity, Identity, Unity, Dependence):

### 🚀 DSPy-Based Optimization (Recommended)

For improved accuracy through automatic prompt optimization, use the **DSPy-based analyzer**:

```bash
# Quick Start: Train an optimized model (uses BootstrapFewShot by default)
python scripts/generate_dspy_model.py \
  output/train_test_sets/data_train.tsv \
  output/train_test_sets/data_test.tsv \
  output/models/optimized_model.json

# Or choose a different optimizer
python scripts/generate_dspy_model.py \
  train.tsv test.tsv output.json \
  --optimizer MIPROv2 \
  --auto heavy

# Batch analyze an ontology using the trained model
python scripts/batch_analyze_dspy.py \
  ontology/guarino_messy.owl \
  --compiled-model output/models/optimized_model.json \
  --model llama3b \
  --output results.tsv

# Or use the trained model in Python
python -c "
from src.llm_clean.ontology.dspy_analyzer import DSPyOntologyAnalyzer
analyzer = DSPyOntologyAnalyzer(
    model='llama3b',
    compiled_model_path='output/models/optimized_model.json'
)
result = analyzer.analyze('Student', 'A person enrolled in a university')
print(result)
"
```

**Optimizer Options** (case-insensitive):

| Optimizer | Speed | Quality | Best For |
|-----------|-------|---------|----------|
| **BootstrapFewShot** (default) | ⚡⚡⚡ Fast | ⭐⭐ Good | Small datasets (10-50 samples) |
| **BootstrapFewShotWithRandomSearch** | ⚡⚡ Moderate | ⭐⭐⭐ Better | Testing variations (20-100 samples) |
| **COPRO** | ⚡⚡ Moderate | ⭐⭐⭐ Better | Instruction optimization (20-100 samples) |
| **MIPROv2** | ⚡ Slow | ⭐⭐⭐⭐ Best | Large datasets (100+ samples) |

> **Note:** The Makefile `generate-anthropic-dspy-models`, `generate-anthropic-dspy-agent-models`, and all `batch-non-agent-dspy-*` aggregate targets are restricted to **BootstrapFewShot only** to keep cost and runtime practical. Other optimizers can still be run individually, e.g. `make generate-anthropic-COPRO-dspy-model`.

```bash
# Examples with different optimizers (case-insensitive)
python scripts/generate_dspy_model.py train.tsv test.tsv out.json --optimizer bootstrapfewshot
python scripts/generate_dspy_model.py train.tsv test.tsv out.json --optimizer bootstrap-few-shot-with-random-search
python scripts/generate_dspy_model.py train.tsv test.tsv out.json --optimizer COPRO --breadth 12
python scripts/generate_dspy_model.py train.tsv test.tsv out.json --optimizer mipro_v2 --auto heavy
```

**📖 Full DSPy Guide**: See [docs/DSPY_GUIDE.md](docs/DSPY_GUIDE.md) for complete documentation on:
- Data preparation and train/test splitting
- Choosing the right optimizer for your dataset
- Optimizer-specific parameters and tuning
- Using trained models for inference
- Evaluation and comparison workflows

**Benefits of DSPy:**
- ✅ Automatic prompt optimization based on training data
- ✅ Multiple optimizer options for different use cases
- ✅ Reproducible and measurable improvements
- ✅ Works across different model types (Llama, Gemini, Claude, GPT-4, etc.)
- ✅ No manual prompt engineering required
- ✅ Defaults optimized for small datasets (~20 samples)

---

### 🤖 DSPy Agent-Based Analyzer

`src/llm_clean/ontology/dspy_agent_analyzer.py` provides an agent-based variant of the DSPy analyzer where **each meta-property is evaluated by a dedicated ReAct agent**. Each agent can call ontology-definition tools before committing to a value, enabling more deliberate, step-by-step reasoning per property.

**Architecture:**

| Component | Role |
|---|---|
| `get_property_definition(property_name)` | Tool — returns the formal OntoClean definition for a property |
| `get_property_examples(property_name)` | Tool — returns canonical positive/negative examples |
| `check_constraints(property_name, value, context)` | Tool — validates OntoClean constraints (e.g. +O → +I) |
| `DSPyRigiditySignature` → `ReAct` agent | Evaluates rigidity (+R / -R / ~R) |
| `DSPyIdentitySignature` → `ReAct` agent | Evaluates identity (+I / -I) |
| `DSPyOwnIdentitySignature` → `ReAct` agent | Evaluates own_identity (+O / -O); receives the identity result as input to enforce the +O → +I constraint |
| `DSPyUnitySignature` → `ReAct` agent | Evaluates unity (+U / -U / ~U) |
| `DSPyDependenceSignature` → `ReAct` agent | Evaluates dependence (+D / -D) |
| `DSPyClassifySignature` → `ChainOfThought` | Derives the classification and overall reasoning from the five values |
| `DSPyAgentOntologyAnalysisModule` | Orchestrates the five agents sequentially |
| `DSPyAgentOntologyAnalyzer` | Public-facing class — same interface as `DSPyOntologyAnalyzer` |

Agents run sequentially: Rigidity → Identity → Own Identity → Unity → Dependence → Classify. The Own Identity agent receives the already-determined Identity value so it can call `check_constraints` to detect the +O → +I violation at inference time.

**Generating an optimized agent model:**

```bash
# Train with BootstrapFewShot (default, recommended for small datasets)
python scripts/generate_dspy_agent_model.py \
  output/train_test_sets/data_train.tsv \
  output/train_test_sets/data_test.tsv \
  --output output/dspy_models/guarino_agent_model.json \
  --model gemini

# Train with MIPROv2 and evaluate before/after
python scripts/generate_dspy_agent_model.py \
  output/train_test_sets/data_train.tsv \
  output/train_test_sets/data_test.tsv \
  --output output/dspy_models/guarino_agent_mipro.json \
  --model gemini \
  --optimizer MIPROv2 \
  --auto medium \
  --evaluate-before \
  --evaluate-after
```

**Additional parameter:** `--max-iters N` controls the maximum number of ReAct iterations per property agent (default: 5).

**Generating agent models via Make:**

```bash
# Single model + optimizer combination
make generate-gemini-BootstrapFewShot-dspy-agent-model
make generate-anthropic-MIPROv2-dspy-agent-model

# All four optimizers for a specific model
make generate-gemini-dspy-agent-models
make generate-anthropic-dspy-agent-models
make generate-llama70b-dspy-agent-models
make generate-qwen72b-dspy-agent-models
make generate-gpt4o-mini-dspy-agent-models
make generate-mistral-small-dspy-agent-models

# All large models (anthropic, gemini, llama70b, qwen72b)
make generate-large-llm-dspy-agent-models

# All small models (gemma9b, qwen7b, llama8b, llama3b, gpt4o-mini, mistral-small)
make generate-small-llm-dspy-agent-models
```

Output files are saved to `output/dspy_models/` with the suffix `_agent_model.json`, e.g. `guarino_gemini_BootstrapFewShot_agent_model.json`.

**Using the agent analyzer in Python:**

```python
from src.llm_clean.ontology.dspy_agent_analyzer import DSPyAgentOntologyAnalyzer

# Base model (no optimization)
analyzer = DSPyAgentOntologyAnalyzer(model="gemini")
result = analyzer.analyze("Student", description="A person enrolled in a university")
print(result)
# {
#   "properties": {"rigidity": "~R", "identity": "+I", "own_identity": "-O",
#                  "unity": "+U", "dependence": "+D"},
#   "classification": "Role",
#   "reasoning": "..."
# }

# With an optimized model
analyzer = DSPyAgentOntologyAnalyzer(
    model="gemini",
    optimized_module_path="output/dspy_models/guarino_agent_model.json"
)
result = analyzer.analyze("Person", description="A human being")
```

**Running the test suite:**

```bash
# Runs tool tests and constraint tests (no API calls), then basic analysis
python src/llm_clean/ontology/test_dspy_agent_analyzer.py
```

The test suite covers:
- **Tool tests** — verifies all five property definition and example tools return content
- **Constraint tests** — verifies `check_constraints` detects +O/−I violations and passes valid combinations
- **Basic analysis** — runs the full agent pipeline on Student, Person, Red, and Employee and validates all output values are in their legal sets

---

### 🤖🔍 DSPy Agent+Critic Analyzer

`src/llm_clean/ontology/dspy_agent_critic_analyzer.py` extends the agent-based analyzer with a **critic feedback loop** for each property. After the ReAct agent produces a value, a `Predict`-based critic validates it. If the critic rejects the result, it provides actionable feedback and the agent reruns — up to `max_critique_attempts` times per property.

**Architecture:**

| Component | Role |
|---|---|
| `DSPyRigiditySignature` → `ReAct` agent | Evaluates rigidity (+R / -R / ~R) |
| `DSPyCriticSignature` → `Predict` critic | Validates the agent's proposed value and reasoning |
| `_run_with_critique(agent, critic, ...)` | Feedback loop helper — retries agent up to `max_critique_attempts` times on REJECT |
| `DSPyAgentCriticOntologyAnalysisModule` | Orchestrates five property agents (each with a dedicated critic) then classifies |
| `DSPyAgentCriticOntologyAnalyzer` | Public-facing class — compatible with `DSPyAgentOntologyAnalyzer`; adds `critique_info` to results |

The same five property agents and tools as the base agent analyzer are used. The critic for each property receives the proposed value and reasoning and outputs `APPROVE` or `REJECT` with feedback. On rejection, the feedback is appended to the agent's description for the next attempt.

The `analyze()` return dict includes an extra `critique_info` key:

```python
{
    "properties": { "rigidity": "~R", ... },
    "classification": "Role",
    "reasoning": "...",
    "critique_info": {
        "rigidity_attempts":  1,   "rigidity_feedback":  "...", "rigidity_approved":  True,
        "identity_attempts":  2,   "identity_feedback":  "...", "identity_approved":  True,
        "own_identity_attempts": 1, ...
        "unity_attempts":     1,   ...
        "dependence_attempts": 3,  "dependence_approved": False,  # max attempts hit
    }
}
```

**Generating an optimized agent+critic model:**

```bash
# Train with BootstrapFewShot (default), 3 critique attempts per property
python scripts/generate_dspy_agent_critic_model.py \
  output/train_test_sets/data_train.tsv \
  output/train_test_sets/data_test.tsv \
  --output output/dspy_models/guarino_agent_critic_model.json \
  --model gemini \
  --max-critique-attempts 3

# Train with MIPROv2, evaluate before/after
python scripts/generate_dspy_agent_critic_model.py \
  output/train_test_sets/data_train.tsv \
  output/train_test_sets/data_test.tsv \
  --output output/dspy_models/guarino_agent_critic_mipro.json \
  --model gemini \
  --optimizer MIPROv2 \
  --auto medium \
  --evaluate-before \
  --evaluate-after
```

**Generating agent+critic models via Make:**

```bash
# Single model + optimizer combination
make generate-gemini-BootstrapFewShot-dspy-agent-critic-model
make generate-anthropic-BootstrapFewShot-dspy-agent-critic-model

# All optimizers for a specific model
make generate-gemini-dspy-agent-critic-models
make generate-anthropic-dspy-agent-critic-models
make generate-llama70b-dspy-agent-critic-models

# All large models (anthropic, gemini, llama70b, qwen72b)
make generate-large-llm-dspy-agent-critic-models

# All small models (gemma9b, qwen7b, llama8b, llama3b, gpt4o-mini, mistral-small)
make generate-small-llm-dspy-agent-critic-models
```

Output files are saved to `output/dspy_models/` with the suffix `_agent_critic_model.json`, e.g. `guarino_gemini_BootstrapFewShot_agent_critic_model.json`.

**Using the agent+critic analyzer in Python:**

```python
from src.llm_clean.ontology.dspy_agent_critic_analyzer import DSPyAgentCriticOntologyAnalyzer

# Base model, 3 critique attempts per property
analyzer = DSPyAgentCriticOntologyAnalyzer(model="gemini", max_critique_attempts=3)
result = analyzer.analyze("Student", description="A person enrolled in a university")
print(result["properties"])    # {"rigidity": "~R", ...}
print(result["critique_info"]) # per-property attempt counts and approval status

# With an optimized model
analyzer = DSPyAgentCriticOntologyAnalyzer(
    model="gemini",
    optimized_module_path="output/dspy_models/guarino_agent_critic_model.json",
    max_critique_attempts=3,
)
result = analyzer.analyze("Person", description="A human being")
```

**Running the test suite:**

```bash
# Runs all non-LLM tests (signature, mock critic loop, tools, constraints, critique_info structure)
# then basic analysis with LLM calls
python src/llm_clean/ontology/test_dspy_agent_critic_analyzer.py
```

The test suite covers:
- **Signature tests** — verifies `DSPyCriticSignature` has all expected input/output fields
- **Mock critic loop** — verifies `_run_with_critique` approve-on-first-attempt, reject-then-approve, and max-attempts-reached scenarios without LLM calls
- **Tool tests** — all five property definition and example tools return content
- **Constraint tests** — `check_constraints` detects +O/−I violations correctly
- **`critique_info` structure** — verifies the analyze() return dict contains all expected per-property keys
- **Basic analysis** — full pipeline on Student, Person, Red, and Employee with live LLM calls

---

### 🔧 Local Fine-Tuning (Apple Silicon / macOS)

Produces a fine-tuned Ollama model from `ground_truth.tsv` in two stages:
1. Generate training data (once)
2. Run the automated fine-tuning pipeline

**Stage 1 — Generate fine-tuning data**

```bash
# Use a strong model to generate reasoning traces (labels come from ground truth)
uv run scripts/generate_finetune_data.py --model anthropic

# Or with Gemini (faster/cheaper)
uv run scripts/generate_finetune_data.py --model gemini

# Test without API calls
uv run scripts/generate_finetune_data.py --skip-reasoning
```

Output: `output/fine-tunning/data/finetune_data.jsonl` — chat-format JSONL with ground-truth property values and LLM-generated reasoning traces.

> A pre-generated copy (22 examples, Gemini reasoning) is already included at `output/fine-tunning/data/finetune_data.jsonl`. Skip Stage 1 and run Stage 2 directly.

**Stage 2 — Run the fine-tuning pipeline**

```bash
# Full pipeline with defaults (Mistral-7B-Instruct-v0.3 → mistral7b-ontoclean Ollama model)
python scripts/finetune_local.py

# Preview all commands without executing
python scripts/finetune_local.py --dry-run

# Resume after a step already completed
python scripts/finetune_local.py --skip-download --skip-train

# Use a different base model
python scripts/finetune_local.py \
  --hf-model Qwen/Qwen2.5-7B-Instruct \
  --ollama-name qwen7b-ontoclean
```

`finetune_local.py` runs four steps automatically:

| Step | Tool | Output |
|------|------|--------|
| 1 — Download & convert | `mlx_lm.convert` | `output/fine-tunning/models/mistral-7b-mlx/` |
| 2 — LoRA fine-tune | `mlx_lm.lora` | `output/fine-tunning/adapters/mistral7b-ontoclean/` |
| 3 — Fuse + export GGUF | `mlx_lm.fuse --export-gguf` | `output/fine-tunning/models/mistral7b-ontoclean.gguf` |
| 4 — Register model | `ollama create` | `ollama run mistral7b-ontoclean` |

Each step is skipped automatically if its output already exists.

**Hardware requirements:**

| Model | Min unified RAM | Notes |
|-------|----------------|-------|
| Mistral-7B | ~16 GB | Practical on most M-series MacBooks |
| Mistral Small 24B | ~48 GB | Requires M2/M3 Ultra or higher |

**Dependencies** (installed automatically on macOS via `uv sync`, skipped on Linux/Windows):

`mlx-lm`, `transformers`, `sentencepiece`, `safetensors`, `gguf`, `llama-cpp-python`

---

### Traditional Analysis Modes

For direct inference without optimization, LLM-Clean provides two primary modes:

### 1. Analysis Modes

#### **Standard Mode (All-at-once)**
The model is prompted to predict all meta-properties in a single pass. This is faster and more cost-effective but may miss subtle nuances.
```bash
# Analyze a single entity
uv run scripts/analyze_entity.py "Student" --desc "A person enrolled in an educational institution"

# Batch analyze an OWL file
uv run scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl --output output/analyzed_entities/results.tsv
```

#### **Agentic Mode (Property-by-property)**
Uses specialized agents for each property. The workflow triggers a separate LLM call for each meta-property, ensuring the model focuses exclusively on the specific criteria for that property.
```bash
# Analyze a single entity with specialized agents
uv run scripts/analyze_entity_agents.py "Student" --verbose

# Batch analyze an OWL file with specialized agents
uv run scripts/batch_analyze_owl_agents.py output/ontologies/guarino_messy.owl --output output/analyzed_entities/agent_results.tsv
```

#### **Batch Analysis Tools**

Three tools are provided for batch analyzing OWL files:

**`batch_analyze_dspy.py`** - DSPy-optimized analyzer (recommended):
```bash
# Using a pre-trained optimized model
python scripts/batch_analyze_dspy.py \
  ontology/guarino_messy.owl \
  --compiled-model output/models/optimized_llama3b.json \
  --model llama3b \
  --output results.tsv

# Using base model without optimization
python scripts/batch_analyze_dspy.py ontology.owl \
  --model llama8b \
  --output results.tsv

# With runtime optimization
python scripts/batch_analyze_dspy.py ontology.owl \
  --train-file train.tsv \
  --test-file test.tsv \
  --optimize-mode medium \
  --output results.tsv
```

**`batch_analyze_agent_dspy.py`** - DSPy agent-based analyzer (per-property ReAct agents):
```bash
# Using a pre-trained optimized agent model
python scripts/batch_analyze_agent_dspy.py \
  ontology/guarino_messy.owl \
  --compiled-model output/dspy_models/guarino_claude_BootstrapFewShot_agent_model.json \
  --model llama3b \
  --output results.tsv

# Using base agent model without optimization
python scripts/batch_analyze_agent_dspy.py ontology.owl \
  --model gemini \
  --output results.tsv
```

**Makefile targets** (use compiled agent model + inference model):
```bash
make batch-agent-dspy-anthropic-BootstrapFewShot-llama3b
make batch-agent-dspy-gemini-BootstrapFewShot-gemma9b
make batch-agent-dspy-anthropic-small-models   # all 8 inference models, Claude-trained
make batch-agent-dspy-gemini-small-models      # all 8 inference models, Gemini-trained
make batch-agent-dspy-small-models             # both of the above
```

**`batch_analyze_agent_critic_dspy.py`** - DSPy agent+critic analyzer (per-property ReAct agents with critic feedback loop):
```bash
# Using a pre-trained optimized agent+critic model
python scripts/batch_analyze_agent_critic_dspy.py \
  ontology/guarino_messy.owl \
  --compiled-model output/dspy_models/guarino_claude_BootstrapFewShot_agent_critic_model.json \
  --model llama3b \
  --max-critique-attempts 3 \
  --output results.tsv

# Using base agent+critic model without optimization
python scripts/batch_analyze_agent_critic_dspy.py ontology.owl \
  --model gemini \
  --max-critique-attempts 2 \
  --output results.tsv
```

**Makefile targets** (use compiled agent+critic model + inference model):
```bash
make batch-agent-critic-dspy-anthropic-BootstrapFewShot-llama3b
make batch-agent-critic-dspy-gemini-BootstrapFewShot-gemma9b
make batch-agent-critic-dspy-anthropic-small-models   # all 8 inference models, Claude-trained
make batch-agent-critic-dspy-gemini-small-models      # all 8 inference models, Gemini-trained
make batch-agent-critic-dspy-small-models             # both of the above
```

**`batch_analyze_owl.py`** - Standard rdflib-based parser:
```bash
# Basic batch analysis
uv run scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl --output results.tsv

# With specific model and background context
uv run scripts/batch_analyze_owl.py input.owl \
  --model anthropic \
  --background-file data/raw/converted_text_files/guarino_text_files/01-guarino00formal-converted-corrected.txt \
  --output results.json \
  --format json

# Test with limited entities
uv run scripts/batch_analyze_owl.py input.owl --limit 5
```

**`batch_analyze_owl_hybrid.py`** - Enhanced parser with Groovy/OWLAPI fallback:
```bash
# Attempts Groovy/OWLAPI first, automatically falls back to rdflib if needed
uv run scripts/batch_analyze_owl_hybrid.py output/ontologies/guarino_messy.owl --output results.tsv
```

**Common Options:**
- `--format {tsv,json}`: Output format (default: tsv)
- `--output FILE`: Save results to file (default: stdout)
- `--model MODEL`: LLM model to use (default: gemini-3-flash-preview, also supports shortcuts: `gemini`, `anthropic`)
- `--background-file FILE`: Path to background text/PDF for contextual analysis
- `--limit N`: Analyze only first N entities (useful for testing)

**Output includes:**
- Term name and URI
- All five meta-properties (rigidity, identity, own_identity, unity, dependence)
- OntoClean classification
- Reasoning/justification

#### **Agent-Based Batch Analysis with Critic Validation**

**`batch_analyze_owl_agents_critic.py`** - Uses specialized agents with critic feedback loop:

This tool combines the agent-based approach (separate specialized agents for each property) with critic validation. Each agent's analysis is validated by a critic, and rejected analyses trigger re-analysis with feedback.

```bash
# Basic usage with critic validation
uv run scripts/batch_analyze_owl_agents_critic.py \
  output/ontologies/guarino_messy.owl \
  --output results_with_critic.tsv

# With specific model and max critique attempts
uv run scripts/batch_analyze_owl_agents_critic.py \
  output/ontologies/guarino_messy.owl \
  --model anthropic \
  --max-critique-attempts 5 \
  --output results_claude_critic.tsv

# With background files
uv run scripts/batch_analyze_owl_agents_critic.py \
  output/ontologies/guarino_messy.owl \
  --default-background-file-type augmented \
  --max-critique-attempts 3 \
  --output results_critic.tsv
```

**Critic-Specific Options:**
- `--max-critique-attempts N`: Maximum re-analysis attempts per property (default: 3)

**Extended Output:**
In addition to standard output, includes critique attempt counts:
- Individual property attempt counts (e.g., `rigidity_attempts`, `identity_attempts`)
- `total_critique_attempts`: Sum of all critique attempts across properties

**Trade-offs:**
- **Pros**: Higher quality through validation, self-correcting with feedback
- **Cons**: Slower execution, more API calls (2-6x per property), higher cost

### 2. Contextual Background Options

The analysis can be grounded in the original Guarino & Welty (2000) paper using two strategies:

#### **Full Source Text**
Provide the entire corrected text of the paper as context.
```bash
uv run scripts/analyze_entity.py "Student" --background-file data/raw/converted_text_files/guarino_text_files/01-guarino00formal-converted-corrected.txt
```

#### **Sectioned Context (Default for Agentic Mode)**
The `AgentOntologyAnalyzer` automatically uses property-specific sections of the paper (e.g., just the "Rigidity" section for rigidity analysis). This minimizes "distraction" from unrelated parts of the text.
- **Default**: Uses augmented sections with introduction context (e.g., `01-guarino00formal-introduction-rigidity.txt`)
- **Alternative**: Switch to simpler sections with `default_background_file_type='simple'`
- Section files are located in: `data/raw/converted_text_files/guarino_text_files/`
- Custom sections can be provided via flags: `--rigidity-background`, `--identity-background`, etc.

### 3. Evaluating Analysis Results

After analyzing entities, you can evaluate predictions against ground truth data and aggregate results across multiple evaluations.

#### **Single Evaluation**
Compare predictions to ground truth and optionally save detailed results as JSON:
```bash
# Display evaluation metrics
python scripts/evaluate_analysis.py predictions.tsv ground_truth.tsv

# Save detailed results as JSON
python scripts/evaluate_analysis.py predictions.tsv ground_truth.tsv --output evaluation.json
```

The JSON output includes:
- Overall accuracy metrics for each meta-property
- Per-term detailed comparisons (predicted vs. ground truth)
- Exact match statistics

#### **Classification Metrics Evaluation**
For more detailed classification metrics (precision, recall, F1-score) with confusion matrix analysis:
```bash
# Display comprehensive classification metrics
python scripts/evaluate_classification_metrics.py predictions.tsv ground_truth.tsv

# Save to JSON
python scripts/evaluate_classification_metrics.py predictions.tsv ground_truth.tsv \
  --output metrics.json

# Save to CSV with agent name
python scripts/evaluate_classification_metrics.py predictions.tsv ground_truth.tsv \
  --output metrics.csv \
  --agent-name "gemini-critic"

# Save to TSV
python scripts/evaluate_classification_metrics.py predictions.tsv ground_truth.tsv \
  --output metrics.tsv

# Save to Markdown
python scripts/evaluate_classification_metrics.py predictions.tsv ground_truth.tsv \
  --output metrics.md
```

**Supported output formats:** `json`, `csv`, `tsv`, `md` (determined by file extension)

**Metrics calculated:**
- **Per-class metrics**: Accuracy, Precision, Recall, F1-Score, Support, TP, FP, TN, FN for each property value (e.g., +R, -R, ~R)
- **Macro-averaged metrics**: Aggregated metrics across all classes for each property
- **Overall metrics**: Aggregated metrics across all properties

**Accuracy calculation:** All accuracy values use the confusion matrix formula: `(TP + TN) / (TP + FP + TN + FN)`

**Console output includes:**
- Property-level breakdown with per-class metrics
- Overall summary statistics
- Easy-to-read formatted tables

**File output includes:**
- Structured data for further analysis
- Complete confusion matrix values for each class
- Aggregate statistics for macro and overall levels

#### **Aggregate Multiple Evaluations**
Collect and compare results from multiple evaluation runs (e.g., different models):
```bash
# Compare two models
python scripts/collect_evaluations.py \
  --files eval_gemini.json eval_claude.json \
  --indexes gemini-flash claude-sonnet \
  --output comparison.csv

# Compare multiple models with custom format
python scripts/collect_evaluations.py \
  --files eval1.json eval2.json eval3.json \
  --indexes model1 model2 model3 \
  --output results.tsv \
  --output-format tsv
```

Supported output formats: `csv`, `tsv`, `md` (markdown table), `json`. Format can be inferred from file extension or specified with `--output-format`.

---

## 🧪 Taxonomy Benchmarking
Runs 13 different models (Gemini, Claude, GPT-4, Llama, etc.) on 10 domains.
```bash
uv run scripts/run_benchmark.py
```
*Results are saved in `docs/reports/BENCHMARK_REPORT.md`.*

### 2. Agentic Workflow (Critic Mode)
Runs a self-critiquing workflow where a model acts as both Taxonomist and Ontological Critic.
```bash
uv run scripts/run_agentic_benchmark.py
```
*Comparison results are in `docs/reports/AGENTIC_BENCHMARK_REPORT.md`.*

---

## 🐳 Docker Usage

Ensure you have a `.env` file in the root directory.

**Using Docker Compose (Recommended):**
```bash
docker-compose up -d
docker-compose exec app ./reproduce.sh
```

**Manual Build:**
```bash
docker build -t llm-clean .
docker run -it --env-file .env llm-clean bash
```

---

## 📜 Key Methodology: OntoClean

LLM-Clean detects violations such as:
- **Rigidity Violation**: `Person` (+R) is-a `Student` (~R). (Rigid child of an Anti-Rigid parent).
- **Constitution Trap**: `Ring` is-a `Gold`. (Material constitution mistaken for inheritance).

By using an Agentic Critique, small models (e.g., Llama 3 8B) can achieve performance comparable to much larger models by explicitly checking their own logic against these formal constraints.

---

## 📝 Citation
If you use this work in your research, please cite the corresponding paper (see `docs/reports/` for details).
