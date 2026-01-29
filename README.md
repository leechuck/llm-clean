# Guarino & Welty Ontology Project + Stevens et al. Reproduction

## Project Overview
This repository contains tools for ontological analysis using LLMs, focusing on two main areas:
1.  **Guarino & Welty (2000)**: Methodologies for "A Formal Ontology of Properties" (OntoClean).
2.  **Stevens et al. (2019)**: Reproduction of an empirical study on upper ontology classification.

## Directory Structure

*   **`experiments/stevens_repro/`**: Code and data for the Stevens et al. reproduction study.
    *   See [experiments/stevens_repro/README.md](experiments/stevens_repro/README.md) for details.
*   **`ontology_tools/`**: Shared Python library for LLM interaction and classification.
*   **`scripts/`**: Core scripts for the Guarino & Welty work (downloading paper, generating messy taxonomy, analyzing entities for meta-properties).
*   **`ontology/`**: Generated OWL files for the Guarino project.
*   **`resources/`**: Shared resources (PDFs, etc.).

## 1. Guarino & Welty (OntoClean)
Tools to analyze arbitrary entities and assign ontological meta-properties (Rigidity, Identity, Unity, Dependence).

*   **Run Analysis**:
    ```bash
    uv run scripts/analyze_entity.py "Student" --desc "A person enrolled in a university"
    ```

## 2. Stevens et al. Reproduction
An experiment to classify travel domain entities into BFO, DOLCE, and UFO using LLMs.

*   **Run Experiment**:
    ```bash
    python3 experiments/stevens_repro/scripts/run_experiment.py
    ```

## Prerequisites
* [uv](https://github.com/astral-sh/uv) (recommended) or Python 3.
* [python-dotenv](https://pypi.org/project/python-dotenv/)
* In the `.env` file, you specify the api keys.
  * Set `OPENROUTER_API_KEY` if you only a general api key.
  * Set `ANTHROPIC_API_KEY` for Anthropic.
  * Set `GOOGLE_API_KEY` for `GEMINI_API_KEY` for Gemini.