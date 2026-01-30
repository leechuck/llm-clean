# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains tools for ontological analysis using LLMs, with two main research areas:

1. **Guarino & Welty (2000) OntoClean**: Analyzing entities using ontological meta-properties (Rigidity, Identity, Unity, Dependence)
2. **Stevens et al. (2019) Reproduction**: Classifying travel domain entities into upper ontologies (BFO, DOLCE, UFO)

## Environment Setup

**API Keys**: The analyzer supports multiple API key configurations depending on the model used. Create a `.env` file in the project root:

```
# For shorthand "gemini" model (default)
GOOGLE_API_KEY=your_google_api_key_here
# OR
GEMINI_API_KEY=your_gemini_api_key_here

# For shorthand "anthropic" model
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# For full model names (google/gemini-3-flash-preview, anthropic/claude-4.5-sonnet, etc.)
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

**Dependencies**: Install via `pip install -r requirements.txt` (requires: rdflib, requests, python-dotenv, tqdm)

**Supported Models**:
- `gemini` - Shorthand for `google/gemini-3-flash-preview` (default for both OntologyAnalyzer and OntologyClassifier), uses GOOGLE_API_KEY or GEMINI_API_KEY
- `anthropic` - Shorthand for `anthropic/claude-4.5-sonnet`, uses ANTHROPIC_API_KEY
- `google/gemini-3-flash-preview` - Full model name, uses OPENROUTER_API_KEY
- `anthropic/claude-4.5-sonnet` - Full model name, uses OPENROUTER_API_KEY
- `openai/gpt-4o` - Full model name (OntologyClassifier only), uses OPENROUTER_API_KEY

## Common Commands

### Guarino & Welty OntoClean Analysis

Analyze a single entity for ontological meta-properties:
```bash
# Uses default "gemini" model
uv run scripts/analyze_entity.py "Student" --desc "A person enrolled in a university"

# Use Anthropic Claude (shorthand)
uv run scripts/analyze_entity.py "Employee" --desc "Person working for organization" --model anthropic

# Use full model name with OpenRouter
uv run scripts/analyze_entity.py "Employee" --desc "Person working for organization" --model anthropic/claude-4.5-sonnet
```

Batch analyze entities from an OWL file:
```bash
# Uses default "gemini" model
python3 scripts/batch_analyze_owl.py path/to/ontology.owl --output results.tsv

# Use Anthropic Claude (shorthand)
python3 scripts/batch_analyze_owl.py path/to/ontology.owl --format json --output results.json --model anthropic
```

### Stevens et al. Reproduction Experiment

Run the full classification experiment:
```bash
# Uses default "gemini" model
python3 experiments/stevens_repro/scripts/run_experiment.py

# Test on first 5 terms with Anthropic Claude (shorthand)
python3 experiments/stevens_repro/scripts/run_experiment.py --limit 5 --model anthropic

# Use OpenAI GPT-4o
python3 experiments/stevens_repro/scripts/run_experiment.py --model openai/gpt-4o
```

Convert results to TSV format:
```bash
python3 experiments/stevens_repro/scripts/results_to_tsv.py
```

## Architecture

### Core Library: `ontology_tools/`

**`OntologyAnalyzer`** (analyzer.py:7-115)
- Uses OpenRouter API to analyze entities for Guarino & Welty meta-properties
- Returns JSON with properties (rigidity, identity, own_identity, unity, dependence), classification, and reasoning
- Default model: `gemini` (shorthand that resolves to `google/gemini-3-flash-preview`)
- Supports shorthand model names with native API key variables:
  - `gemini` → uses GOOGLE_API_KEY or GEMINI_API_KEY
  - `anthropic` → uses ANTHROPIC_API_KEY, resolves to `anthropic/claude-4.5-sonnet`
- Full model names (e.g., `google/gemini-3-flash-preview`, `anthropic/claude-4.5-sonnet`) use OPENROUTER_API_KEY
- Model validation enforced at initialization (raises ValueError for unsupported models)
- Uses python-dotenv to load API keys from `.env` file
- All models use OpenRouter API endpoint regardless of shorthand vs full name
- Includes robust JSON parsing with:
  - Markdown code fence removal (handles ` ```json ... ``` ` wrappers)
  - Trailing comma cleanup

**`OntologyClassifier`** (classifier.py:8-125)
- Implements two classification strategies:
  - **One-shot**: Present all ontology classes at once, select best match
  - **Hierarchical**: Traverse ontology tree from root, selecting best subclass at each level
- Default model: `gemini` (shorthand that resolves to `google/gemini-3-flash-preview`)
- Supports shorthand model names with native API key variables:
  - `gemini` → uses GOOGLE_API_KEY or GEMINI_API_KEY
  - `anthropic` → uses ANTHROPIC_API_KEY, resolves to `anthropic/claude-4.5-sonnet`
- Full model names (e.g., `google/gemini-3-flash-preview`, `anthropic/claude-4.5-sonnet`, `openai/gpt-4o`) use OPENROUTER_API_KEY
- Model validation enforced at initialization (raises ValueError for unsupported models)
- Uses python-dotenv to load API keys from `.env` file
- All models use OpenRouter API endpoint regardless of shorthand vs full name
- Includes exponential backoff for rate limiting (429 errors)
- Robust JSON parsing with:
  - Markdown code fence removal (handles ` ```json ... ``` ` wrappers)
  - Trailing comma cleanup

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
- `batch_analyze_owl_hybrid.py`: Attempts to use Groovy/OWLAPI for entity extraction, automatically falls back to rdflib if Groovy dependencies fail. Provides more robust OWL parsing when Groovy is configured properly, but works reliably even when it's not.

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
