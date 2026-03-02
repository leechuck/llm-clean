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

---

## 🧪 Benchmarking

LLM-Clean evaluates models based on their adherence to OntoClean constraints (Rigidity, Identity, Unity, Dependence).

### 1. Zero-Shot Benchmark
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
