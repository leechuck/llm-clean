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
- **Complete Workflows**: `all`, `reproduce-batch`

Run `make help` to see the full list with descriptions.

## 🧪 OntoClean Property Analysis

LLM-Clean provides two primary modes for analyzing entity meta-properties (Rigidity, Identity, Unity, Dependence).

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

Two tools are provided for batch analyzing OWL files:

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
