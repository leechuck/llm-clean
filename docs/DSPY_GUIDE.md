# DSPy-Based Ontology Analysis Guide

This guide covers the complete workflow for using DSPy (Declarative Self-improving Language Programs) to optimize ontology analysis models. DSPy allows you to automatically improve LLM pipelines through optimization techniques like MIPROv2.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Data Preparation](#data-preparation)
4. [Model Training & Optimization](#model-training--optimization)
5. [Using Trained Models](#using-trained-models)
6. [Architecture](#architecture)
7. [API Reference](#api-reference)

---

## Overview

### What is DSPy?

DSPy is a framework for algorithmically optimizing language model prompts and weights. Instead of manually tweaking prompts, DSPy:

1. Takes your program signature (inputs/outputs)
2. Uses training examples to optimize the pipeline
3. Produces an improved model that performs better on your task

### Why Use DSPy for Ontology Analysis?

Traditional prompt engineering requires manual iteration. With DSPy:

- **Automatic Optimization**: MIPROv2 optimizer improves prompts based on training data
- **Reproducible**: Deterministic optimization with configurable parameters
- **Scalable**: Works across different model sizes and types
- **Measurable**: Built-in metrics for evaluating improvements

### What You'll Learn

- How to prepare training/test data from existing analysis results
- How to train and optimize ontology analysis models using MIPROv2
- How to use trained models for inference on new entities
- How to evaluate model performance

---

## Quick Start

### Prerequisites

```bash
# Install dependencies (dspy-ai, scikit-learn)
uv sync

# Set up API keys in .env file
cat > .env << EOF
OPENROUTER_API_KEY=your_openrouter_api_key_here
EOF
```

### 30-Second Example

```bash
# 1. Split your data into train/test sets
python scripts/generate_train_test.py \
  data/input.tsv \
  --output-dir output/train_test_sets

# 2. Train an optimized model
python scripts/generate_dspy_model.py \
  output/train_test_sets/input_train.tsv \
  output/train_test_sets/input_test.tsv \
  output/models/optimized_model.json

# 3. Use the trained model
python -c "
from src.llm_clean.ontology.dspy_analyzer import DSPyOntologyAnalyzer
analyzer = DSPyOntologyAnalyzer(
    model='gemini',
    compiled_model_path='output/models/optimized_model.json'
)
result = analyzer.analyze('Student', 'A person enrolled in a university')
print(result)
"
```

---

## Data Preparation

### Required Data Format

Your training data must include:

**Required Fields:**
- `term`: Entity name (e.g., "Student", "Employee")
- `rigidity`: +R (rigid), -R (non-rigid), or ~R (anti-rigid)
- `identity`: +I (has identity) or -I (no identity)
- `own_identity`: +O (provides own identity) or -O (doesn't provide own identity)
- `unity`: +U (is a whole), -U (not necessarily whole), or ~U (anti-unity)
- `dependence`: +D (dependent) or -D (independent)

**Optional Fields:**
- `description`: Entity description
- `usage`: Usage examples or context
- `classification`: OntoClean category (e.g., "Sortal", "Role", "Mixin")
- `reasoning`: Justification for property assignments

### Supported File Formats

#### TSV Format
```tsv
term	description	rigidity	identity	own_identity	unity	dependence	classification	reasoning
Student	A person enrolled in a university	~R	+I	-O	+U	-D	Role	Students are anti-rigid because...
Employee	A person working for an organization	~R	+I	-O	+U	+D	Role	Employees are anti-rigid because...
```

#### CSV Format
```csv
term,description,rigidity,identity,own_identity,unity,dependence,classification,reasoning
Student,A person enrolled in a university,~R,+I,-O,+U,-D,Role,Students are anti-rigid because...
Employee,A person working for an organization,~R,+I,-O,+U,+D,Role,Employees are anti-rigid because...
```

#### JSON Format
```json
[
  {
    "term": "Student",
    "description": "A person enrolled in a university",
    "rigidity": "~R",
    "identity": "+I",
    "own_identity": "-O",
    "unity": "+U",
    "dependence": "-D",
    "classification": "Role",
    "reasoning": "Students are anti-rigid because..."
  },
  {
    "term": "Employee",
    "description": "A person working for an organization",
    "rigidity": "~R",
    "identity": "+I",
    "own_identity": "-O",
    "unity": "+U",
    "dependence": "+D",
    "classification": "Role",
    "reasoning": "Employees are anti-rigid because..."
  }
]
```

### Splitting Your Data

Use the `generate_train_test.py` script to create train/test splits:

```bash
# Basic usage (70/30 split)
python scripts/generate_train_test.py data/my_data.tsv

# Custom split ratio (80/20)
python scripts/generate_train_test.py data/my_data.tsv --train-size 0.8

# Custom output directory
python scripts/generate_train_test.py data/my_data.tsv \
  --output-dir output/my_experiment

# Custom random seed for reproducibility
python scripts/generate_train_test.py data/my_data.tsv --random-state 123

# Convert format during split (TSV -> JSON)
python scripts/generate_train_test.py data/my_data.tsv --output-format json
```

**Script Options:**
- `--train-size`: Fraction for training set (default: 0.7)
- `--random-state`: Random seed (default: 42)
- `--output-dir`: Output directory (default: `output/train_test_sets`)
- `--output-format`: Output format (default: same as input, options: tsv, csv, json)

**Output Files:**
```
output/train_test_sets/
  my_data_train.tsv  # Training set (70% by default)
  my_data_test.tsv   # Test set (30% by default)
```

### Data Quality Recommendations

1. **Minimum Dataset Size**: At least 20-30 examples recommended
2. **Balanced Coverage**: Include diverse entity types (Sortals, Roles, Mixins, etc.)
3. **Clear Descriptions**: Provide descriptive text for better reasoning
4. **Consistent Labels**: Use standard notation (+R/-R/~R, +I/-I, etc.)
5. **Validation**: Review ground truth carefully - optimizer learns from your labels

---

## Model Training & Optimization

### Overview

The `generate_dspy_model.py` script:
1. Loads training and test data
2. Initializes a DSPy module with the specified model
3. Runs MIPROv2 optimization on training data
4. Evaluates the optimized model on test data
5. Saves the compiled model for future use

### Basic Usage

```bash
python scripts/generate_dspy_model.py \
  output/train_test_sets/data_train.tsv \
  output/train_test_sets/data_test.tsv \
  output/models/optimized_model.json
```

### Supported Models

**Model Shortcuts** (use native API keys):
- `gemini` → google/gemini-3-flash-preview (uses GOOGLE_API_KEY or GEMINI_API_KEY)
- `anthropic` → anthropic/claude-4.5-sonnet (uses ANTHROPIC_API_KEY)
- `gemma9b` → google/gemma-2-9b-it
- `qwen7b` → qwen/qwen-2.5-7b-instruct
- `llama3b` → meta-llama/llama-3.2-3b-instruct
- `llama8b` → meta-llama/llama-3.1-8b-instruct

**Full Model Names** (use OPENROUTER_API_KEY):
- `google/gemini-3-flash-preview`
- `anthropic/claude-4.5-sonnet`
- `openai/gpt-4o`
- `meta-llama/llama-3.1-70b-instruct`
- And any other OpenRouter-supported model

### Optimization Modes

MIPROv2 supports three optimization modes:

| Mode | Speed | Quality | Best For |
|------|-------|---------|----------|
| `light` | Fast | Good | Quick experiments, small datasets |
| `medium` | Moderate | Better | General use (default) |
| `heavy` | Slow | Best | Production models, large datasets |

**Example Usage:**

```bash
# Light mode (fast experimentation)
python scripts/generate_dspy_model.py \
  train.tsv test.tsv output.json \
  --optimize-mode light

# Medium mode (balanced, default)
python scripts/generate_dspy_model.py \
  train.tsv test.tsv output.json \
  --optimize-mode medium

# Heavy mode (best quality)
python scripts/generate_dspy_model.py \
  train.tsv test.tsv output.json \
  --optimize-mode heavy
```

### Advanced Options

```bash
python scripts/generate_dspy_model.py \
  train.tsv test.tsv output.json \
  --model anthropic \                    # Use Claude instead of Gemini
  --optimize-mode heavy \                # Thorough optimization
  --skip-pre-eval \                      # Skip initial evaluation
  --skip-post-eval                       # Skip final evaluation
```

**All Options:**
- `train_file`: Path to training data (TSV, CSV, or JSON)
- `test_file`: Path to test data (TSV, CSV, or JSON)
- `output`: Path to save compiled model (JSON format)
- `--model`: LLM model to use (default: `gemini`)
- `--optimize-mode`: Optimization thoroughness (default: `medium`)
- `--skip-pre-eval`: Skip pre-optimization evaluation
- `--skip-post-eval`: Skip post-optimization evaluation

### Understanding the Output

```bash
$ python scripts/generate_dspy_model.py train.tsv test.tsv model.json

Loading training data from train.tsv...
Loaded 14 training examples

Loading test data from test.tsv...
Loaded 7 test examples

Initializing DSPy analyzer with model: gemini
✓ Analyzer initialized successfully

=== Pre-Optimization Evaluation ===
Evaluating base model on test set...
Average Score: 0.4286 (3/7 exact matches)

=== Running Optimization ===
Optimizing with MIPROv2 (mode: medium)...
This may take several minutes...
✓ Optimization complete

=== Post-Optimization Evaluation ===
Evaluating optimized model on test set...
Average Score: 0.7143 (5/7 exact matches)
Improvement: +66.7% (+2 exact matches)

Saving compiled model to model.json...
✓ Model saved successfully

Summary:
--------
Training Examples: 14
Test Examples: 7
Base Model Score: 42.86%
Optimized Model Score: 71.43%
Improvement: +28.57 percentage points
```

### What Gets Saved?

The compiled model file (`output.json`) contains:
- Optimized prompts and demonstrations
- Model configuration
- Optimization parameters
- Performance metrics

This file can be loaded later for inference without re-training.

---

## Using Trained Models

### Python API

```python
from src.llm_clean.ontology.dspy_analyzer import DSPyOntologyAnalyzer

# Load a pre-trained model
analyzer = DSPyOntologyAnalyzer(
    model='gemini',  # Must match the model used for training
    compiled_model_path='output/models/optimized_model.json'
)

# Analyze a single entity
result = analyzer.analyze(
    term='Student',
    description='A person enrolled in a university'
)

# Access results
print(f"Rigidity: {result['rigidity']}")
print(f"Identity: {result['identity']}")
print(f"Classification: {result['classification']}")
print(f"Reasoning: {result['reasoning']}")
```

### Result Format

```python
{
    'rigidity': '~R',
    'identity': '+I',
    'own_identity': '-O',
    'unity': '+U',
    'dependence': '-D',
    'classification': 'Role',
    'reasoning': 'Students are anti-rigid (essential to Person but not to Student itself). They carry identity from Person (+I) but don\'t supply their own identity criterion (-O). Students form wholes (+U) and are existentially independent (-D).'
}
```

### Training Without Pre-Compiled Model

You can also optimize during runtime:

```python
analyzer = DSPyOntologyAnalyzer(
    model='gemini',
    train_file='output/train_test_sets/data_train.tsv',
    test_file='output/train_test_sets/data_test.tsv'
)

# Optimize the model
analyzer.optimize(mode='medium')

# Now use it for analysis
result = analyzer.analyze('Employee', 'A person working for an organization')

# Save for later use
analyzer.module.save('output/models/my_model.json')
```

### Batch Analysis

```python
from src.llm_clean.ontology.dspy_analyzer import DSPyOntologyAnalyzer
import csv

# Load model
analyzer = DSPyOntologyAnalyzer(
    model='gemini',
    compiled_model_path='output/models/optimized_model.json'
)

# Analyze multiple entities
entities = [
    ('Student', 'A person enrolled in a university'),
    ('Employee', 'A person working for an organization'),
    ('Book', 'A written work published as a printed or electronic resource')
]

results = []
for term, desc in entities:
    result = analyzer.analyze(term, desc)
    result['term'] = term
    result['description'] = desc
    results.append(result)

# Save to TSV
with open('output/batch_results.tsv', 'w', newline='') as f:
    writer = csv.DictWriter(f, delimiter='\t', fieldnames=[
        'term', 'description', 'rigidity', 'identity', 'own_identity',
        'unity', 'dependence', 'classification', 'reasoning'
    ])
    writer.writeheader()
    writer.writerows(results)
```

---

## Architecture

### Components

```
src/llm_clean/ontology/
├── dspy_analyzer.py          # Main DSPy analyzer
├── prompts.py                # Centralized prompts
├── analyzer.py               # Traditional analyzer (for comparison)
└── test_dspy_analyzer.py     # Test suite

scripts/
├── generate_train_test.py    # Data splitting tool
└── generate_dspy_model.py    # Model training tool
```

### DSPyOntologyAnalyzer Architecture

```
DSPyOntologyAnalyzer
├── __init__()
│   ├── Initializes DSPy LM (OpenRouter)
│   ├── Creates OntologyAnalysisModule
│   └── Optionally loads compiled model
│
├── analyze(term, description)
│   ├── Runs inference through DSPy module
│   ├── Parses JSON response
│   └── Returns structured results
│
└── optimize(mode)
    ├── Loads training/test examples
    ├── Runs MIPROv2 optimization
    └── Compiles optimized module
```

### OntologyAnalysisModule

```python
class OntologyAnalysisModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog = dspy.ChainOfThought(OntologyAnalysisSignature)
    
    def forward(self, term, description=""):
        return self.prog(term=term, description=description)
```

**Key Features:**
- Uses `dspy.ChainOfThought` for reasoning
- Signature defines inputs (term, description) and outputs (analysis JSON)
- Automatically optimized by MIPROv2

### Optimization Process

```
1. Load Examples
   ├── Parse TSV/CSV/JSON files
   └── Convert to dspy.Example objects

2. Initialize Optimizer
   ├── Create MIPROv2 instance
   ├── Set metric function
   └── Configure optimization mode

3. Run Optimization
   ├── Generate candidate prompts
   ├── Evaluate on training set
   ├── Select best performing variants
   └── Bootstrap demonstrations

4. Compile Module
   ├── Save optimized parameters
   └── Ready for inference
```

### Metric Function

The optimizer uses a custom metric that checks exact match for all properties:

```python
def ontology_metric(example, pred, trace=None):
    """
    Returns 1.0 if all properties match, 0.0 otherwise.
    """
    try:
        pred_json = json.loads(pred.analysis)
        return 1.0 if all([
            pred_json.get('rigidity') == example.rigidity,
            pred_json.get('identity') == example.identity,
            pred_json.get('own_identity') == example.own_identity,
            pred_json.get('unity') == example.unity,
            pred_json.get('dependence') == example.dependence
        ]) else 0.0
    except:
        return 0.0
```

This metric rewards **exact matches only** - all five properties must be correct.

---

## API Reference

### DSPyOntologyAnalyzer

```python
class DSPyOntologyAnalyzer:
    """
    DSPy-based ontology analyzer with MIPROv2 optimization.
    """
    
    def __init__(
        self,
        model: str = "gemini",
        train_file: Optional[str] = None,
        test_file: Optional[str] = None,
        compiled_model_path: Optional[str] = None
    )
```

**Parameters:**
- `model`: Model name (shortcut or full name)
- `train_file`: Path to training data (optional, needed for optimization)
- `test_file`: Path to test data (optional, used for evaluation)
- `compiled_model_path`: Path to pre-trained model (optional)

**Methods:**

#### analyze()
```python
def analyze(
    self,
    term: str,
    description: str = "",
    usage: str = ""
) -> Dict[str, str]
```

Analyzes an entity and returns ontological properties.

**Returns:**
```python
{
    'rigidity': str,      # +R, -R, or ~R
    'identity': str,      # +I or -I
    'own_identity': str,  # +O or -O
    'unity': str,         # +U, -U, or ~U
    'dependence': str,    # +D or -D
    'classification': str,  # e.g., "Sortal", "Role", "Mixin"
    'reasoning': str      # Justification text
}
```

#### optimize()
```python
def optimize(
    self,
    mode: str = "medium"
) -> None
```

Runs MIPROv2 optimization on training data.

**Parameters:**
- `mode`: Optimization mode ('light', 'medium', or 'heavy')

**Requirements:**
- Must have `train_file` and `test_file` set during initialization

#### evaluate()
```python
def evaluate(
    self,
    examples: List[dspy.Example]
) -> float
```

Evaluates model performance on a list of examples.

**Returns:** Average score (0.0 to 1.0)

### generate_train_test.py

```bash
python scripts/generate_train_test.py INPUT_FILE [OPTIONS]
```

**Arguments:**
- `input_file`: Path to input data file (TSV, CSV, or JSON)

**Options:**
- `--train-size FLOAT`: Training set fraction (default: 0.7)
- `--random-state INT`: Random seed (default: 42)
- `--output-dir DIR`: Output directory (default: output/train_test_sets)
- `--output-format {tsv,csv,json}`: Output format (default: same as input)

### generate_dspy_model.py

```bash
python scripts/generate_dspy_model.py TRAIN_FILE TEST_FILE OUTPUT [OPTIONS]
```

**Arguments:**
- `train_file`: Path to training data
- `test_file`: Path to test data  
- `output`: Path to save compiled model

**Options:**
- `--model MODEL`: LLM model to use (default: gemini)
- `--optimize-mode {light,medium,heavy}`: Optimization mode (default: medium)
- `--skip-pre-eval`: Skip pre-optimization evaluation
- `--skip-post-eval`: Skip post-optimization evaluation

---

## Tips & Best Practices

### Data Preparation
1. **Quality over Quantity**: 20 high-quality examples > 100 noisy examples
2. **Diverse Coverage**: Include different entity types and edge cases
3. **Validation**: Double-check ground truth labels before training
4. **Consistent Format**: Stick to one format (TSV recommended for readability)

### Model Selection
1. **Start Small**: Use `gemini` (fast, cost-effective) for initial experiments
2. **Scale Up**: Switch to `anthropic` or `openai/gpt-4o` for production
3. **Match Training**: Use the same model for training and inference

### Optimization
1. **Start Light**: Use `light` mode for quick iterations
2. **Go Medium**: Use `medium` mode for most use cases (good balance)
3. **Go Heavy**: Use `heavy` mode only for final production models
4. **Monitor Progress**: Watch the evaluation scores to see improvement

### Evaluation
1. **Holdout Test Set**: Never train on your test data
2. **Multiple Runs**: Try different random seeds for robustness
3. **Baseline Comparison**: Compare against non-optimized analyzer
4. **Error Analysis**: Examine failures to improve training data

### Production Deployment
1. **Save Models**: Always save compiled models for reuse
2. **Version Control**: Track model versions and training data
3. **Monitor Performance**: Log predictions for continuous improvement
4. **Fallback Strategy**: Keep a baseline model as backup

---

## Troubleshooting

### Common Issues

**Issue: "No training examples loaded"**
- Check that your file has the required columns
- Verify file format matches extension (.tsv, .csv, .json)
- Ensure file is not empty

**Issue: "Unsupported model"**
- Use a supported model shortcut or full model name
- Check that API keys are set in .env file

**Issue: "Optimization takes too long"**
- Use `light` mode for faster results
- Reduce training set size
- Try a faster model (gemini instead of anthropic)

**Issue: "Poor performance after optimization"**
- Check training data quality
- Try `heavy` optimization mode
- Increase training set size
- Verify test set is representative

**Issue: "JSON parsing errors"**
- Model output may be malformed
- Try a different model
- Check that examples in training data are valid

---

## Examples

### Example 1: Complete Workflow

```bash
# Step 1: Split existing analysis results
python scripts/generate_train_test.py \
  output/analyzed_entities/agent_results.tsv \
  --train-size 0.75

# Step 2: Train optimized model
python scripts/generate_dspy_model.py \
  output/train_test_sets/agent_results_train.tsv \
  output/train_test_sets/agent_results_test.tsv \
  output/models/optimized_gemini.json \
  --model gemini \
  --optimize-mode medium

# Step 3: Use trained model
python -c "
from src.llm_clean.ontology.dspy_analyzer import DSPyOntologyAnalyzer
analyzer = DSPyOntologyAnalyzer(
    model='gemini',
    compiled_model_path='output/models/optimized_gemini.json'
)
result = analyzer.analyze('Professor', 'An academic faculty member at a university')
print(f'Classification: {result[\"classification\"]}')
print(f'Reasoning: {result[\"reasoning\"]}')
"
```

### Example 2: Model Comparison

```bash
# Train Gemini model
python scripts/generate_dspy_model.py \
  train.tsv test.tsv output/gemini_model.json \
  --model gemini --optimize-mode medium

# Train Claude model
python scripts/generate_dspy_model.py \
  train.tsv test.tsv output/claude_model.json \
  --model anthropic --optimize-mode medium

# Compare both
python -c "
from src.llm_clean.ontology.dspy_analyzer import DSPyOntologyAnalyzer

gemini = DSPyOntologyAnalyzer('gemini', compiled_model_path='output/gemini_model.json')
claude = DSPyOntologyAnalyzer('anthropic', compiled_model_path='output/claude_model.json')

test_term = 'Employee'
test_desc = 'A person working for an organization'

print('Gemini:', gemini.analyze(test_term, test_desc)['classification'])
print('Claude:', claude.analyze(test_term, test_desc)['classification'])
"
```

### Example 3: Custom Evaluation

```python
from src.llm_clean.ontology.dspy_analyzer import DSPyOntologyAnalyzer
import json

# Load model
analyzer = DSPyOntologyAnalyzer(
    model='gemini',
    compiled_model_path='output/models/optimized_model.json'
)

# Load test data
with open('output/train_test_sets/data_test.json') as f:
    test_data = json.load(f)

# Evaluate
correct = 0
total = len(test_data)

for item in test_data:
    result = analyzer.analyze(item['term'], item.get('description', ''))
    
    # Check if all properties match
    if all([
        result['rigidity'] == item['rigidity'],
        result['identity'] == item['identity'],
        result['own_identity'] == item['own_identity'],
        result['unity'] == item['unity'],
        result['dependence'] == item['dependence']
    ]):
        correct += 1
    else:
        print(f"❌ {item['term']}: Expected {item['classification']}, got {result['classification']}")

accuracy = correct / total
print(f"\n✓ Accuracy: {accuracy:.2%} ({correct}/{total})")
```

---

## Further Reading

- **DSPy Documentation**: https://dspy-docs.vercel.app/
- **MIPROv2 Paper**: Multi-Prompt Instruction Refinement Optimizer
- **Guarino & Welty (2000)**: "Identity and Subsumption" - foundational OntoClean paper
- **OpenRouter API**: https://openrouter.ai/docs

---

## Support

For issues or questions:
- Check this guide's [Troubleshooting](#troubleshooting) section
- Review the [API Reference](#api-reference)
- Examine test files in `src/llm_clean/ontology/test_dspy_analyzer.py`
- Open an issue on GitHub

---

*Last updated: 2025*
