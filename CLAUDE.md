# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains tools for ontological analysis using LLMs, with two main research areas:

1. **Guarino & Welty (2000) OntoClean**: Analyzing entities using ontological meta-properties (Rigidity, Identity, Unity, Dependence)
2. **Stevens et al. (2019) Reproduction**: Classifying travel domain entities into upper ontologies (BFO, DOLCE, UFO)

## Environment Setup

**API Key Required**: All scripts require the `OPENROUTER_API_KEY` environment variable to be set.

**Dependencies**: Install via `pip install -r requirements.txt` (requires: rdflib, requests, tqdm)

## Common Commands

### Guarino & Welty OntoClean Analysis

Analyze a single entity for ontological meta-properties:
```bash
uv run scripts/analyze_entity.py "Student" --desc "A person enrolled in a university"
uv run scripts/analyze_entity.py "Employee" --desc "Person working for organization" --model openai/gpt-4o
```

Batch analyze entities from an OWL file:
```bash
python3 scripts/batch_analyze_owl.py path/to/ontology.owl --output results.tsv
python3 scripts/batch_analyze_owl.py path/to/ontology.owl --format json --output results.json
```

### Stevens et al. Reproduction Experiment

Run the full classification experiment:
```bash
python3 experiments/stevens_repro/scripts/run_experiment.py --model openai/gpt-4o
python3 experiments/stevens_repro/scripts/run_experiment.py --limit 5  # Test on first 5 terms
```

Convert results to TSV format:
```bash
python3 experiments/stevens_repro/scripts/results_to_tsv.py
```

## Architecture

### Core Library: `ontology_tools/`

**`OntologyAnalyzer`** (analyzer.py:6-98)
- Uses OpenRouter API to analyze entities for Guarino & Welty meta-properties
- Returns JSON with properties (rigidity, identity, own_identity, unity, dependence), classification, and reasoning
- Default model: `google/gemini-3-flash-preview`
- Includes retry logic and robust JSON parsing

**`OntologyClassifier`** (classifier.py:7-109)
- Implements two classification strategies:
  - **One-shot**: Present all ontology classes at once, select best match
  - **Hierarchical**: Traverse ontology tree from root, selecting best subclass at each level
- Default model: `openai/gpt-4o`
- Includes exponential backoff for rate limiting (429 errors)

### Stevens Reproduction Structure

**Data Flow**:
1. `data/input_terms.json`: 46 travel domain entities with descriptions
2. `data/ontologies.json`: Class hierarchies, definitions, and examples for BFO, DOLCE, UFO
3. `scripts/run_experiment.py`: Runs both classification strategies for each term against all three ontologies
4. `results/experiment_results.json`: Full results with reasoning traces
5. `scripts/results_to_tsv.py`: Converts JSON to tabular format

**Key Design**: `run_experiment.py` saves results incrementally after each term, allowing resumption if interrupted. It checks for existing results and skips already-processed terms.

### Batch Analysis Scripts

- `batch_analyze_owl.py`: Extracts OWL classes using rdflib, analyzes each with OntologyAnalyzer
- `batch_analyze_owl_hybrid.py`: Variant batch analyzer (check specific implementation if needed)

### Path Resolution Pattern

All scripts use:
```python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```
This allows importing `ontology_tools` from any script location.

## Meta-Properties Framework (Guarino & Welty)

The five meta-properties analyzed:

1. **Rigidity**: +R (rigid/essential), -R (non-rigid), ~R (anti-rigid like Role/Phase)
2. **Identity**: +I (carries identity condition), -I (no identity condition)
3. **Own Identity**: +O (supplies own IC), -O (inherits or lacks IC). Constraint: +O → +I
4. **Unity**: +U (instances are wholes), -U (not necessarily wholes), ~U (anti-unity/aggregates)
5. **Dependence**: +D (depends on something else), -D (independent)

These are used to classify entities into categories like Sortal, Role, Mixin, etc.

## Classification Strategies (Stevens Reproduction)

**Hierarchical Strategy**: Starts at ontology root (e.g., "Entity" in BFO), asks LLM to select best child class. Repeats recursively until reaching a leaf or the LLM chooses to stop at current level. Produces a classification path and reasoning trace.

**One-Shot Strategy**: Presents all ontology classes simultaneously with definitions and examples. LLM selects single best class and provides confidence rating.

Both strategies are run for each (term, ontology) pair to compare approaches.
