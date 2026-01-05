# Guarino & Welty Ontology Project

## Project Overview
This project implements tools related to the methodology described in *"A Formal Ontology of Properties"* by Guarino & Welty (2000). It serves two main purposes:
1.  **Reproducibility**: Automates the retrieval of the original paper and the formalization of its "messy taxonomy" example into a standard OWL ontology.
2.  **Analysis**: Provides an LLM-based CLI tool to analyze arbitrary entities and assign them the ontological meta-properties defined in the paper (Rigidity, Identity, Unity, Dependence).

## Key Technologies
*   **Language**: Python 3
*   **Dependency Management**: `uv`
*   **Ontology**: `rdflib` (for OWL generation)
*   **AI Integration**: OpenRouter API (accessed via `requests`)

## Architecture
*   **`scripts/`**: Contains the core logic.
    *   `download_paper.py`: Downloads the academic paper.
    *   `generate_messy_owl.py`: Generates the `guarino_messy.owl` file using `rdflib`.
    *   `analyze_entity.py`: Connects to OpenRouter to classify terms based on ontological definitions.
*   **`resources/`**: Stores external assets (e.g., the downloaded PDF).
*   **`ontology/`**: Stores generated ontology files.
*   **`reproduce.sh`**: A shell script that orchestrates the download and generation pipeline.

## Building and Running

### Prerequisites
*   [uv](https://github.com/astral-sh/uv) must be installed.
*   For the analysis tool, an `OPENROUTER_API_KEY` environment variable is required.

### 1. Reproduce the Ontology
To download the paper and generate the static ontology file:
```bash
chmod +x reproduce.sh
./reproduce.sh
```
This will create:
*   `resources/01-guarino00formal.pdf`
*   `ontology/guarino_messy.owl`

### 2. Analyze an Entity (LLM)
To analyze a term using an LLM (requires `OPENROUTER_API_KEY`):
```bash
export OPENROUTER_API_KEY="your_key_here"
uv run scripts/analyze_entity.py "Student" --desc "A person enrolled in a university"
```
**Arguments:**
*   `term`: The entity name (required).
*   `--desc`: A description of the entity (optional, but recommended for accuracy).
*   `--usage`: A sentence showing how the term is used (optional).
*   `--model`: The OpenRouter model to use (default: `openai/gpt-4o`).

## Development Conventions
*   **Dependency Management**: Use `uv` to run scripts. Dependencies are defined in `requirements.txt` but `uv` handles them ephemerally or in a venv.
*   **Script Execution**: Prefer `uv run scripts/<script_name>.py` over direct `python` calls to ensure environment consistency.
*   **Output Management**: Scripts should check for/create output directories (`resources`, `ontology`) before writing.
