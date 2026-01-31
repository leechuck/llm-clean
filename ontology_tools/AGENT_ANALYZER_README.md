# Agent-Based Ontology Analyzer

## Overview

The `AgentOntologyAnalyzer` uses **specialized agents** to analyze each ontological meta-property independently. Unlike the standard `OntologyAnalyzer` which analyzes all properties in a single call, the agent-based approach:

1. **Separates concerns**: Each meta-property (Rigidity, Identity, Own Identity, Unity, Dependence) is analyzed by a dedicated agent
2. **Improves focus**: Each agent specializes in understanding one specific meta-property
3. **Enables custom backgrounds**: You can provide different background files for different properties
4. **Uses property-specific defaults**: By default, loads specialized Guarino & Welty text excerpts for each property

## Default Background Files

By default, the analyzer loads property-specific background files:

- **Rigidity**: `resources/converted_text_files/guarino_text_files/01-guarino00formal-rigidity.txt`
- **Identity**: `resources/converted_text_files/guarino_text_files/01-guarino00formal-identity.txt`
- **Own Identity**: `resources/converted_text_files/guarino_text_files/01-guarino00formal-identity.txt`
- **Unity**: `resources/converted_text_files/guarino_text_files/01-guarino00formal-unity.txt`
- **Dependence**: `resources/converted_text_files/guarino_text_files/01-guarino00formal-dependence.txt`

These files contain relevant excerpts from the Guarino & Welty (2000) paper focused on each specific meta-property.

## Architecture

```
AgentOntologyAnalyzer
├── _analyze_rigidity()      → Specialized agent for Rigidity
├── _analyze_identity()       → Specialized agent for Identity
├── _analyze_own_identity()   → Specialized agent for Own Identity
├── _analyze_unity()          → Specialized agent for Unity
├── _analyze_dependence()     → Specialized agent for Dependence
└── analyze()                 → Orchestrates all agents
```

## Usage

### Basic Usage (With Default Property-Specific Backgrounds)

```python
from ontology_tools.agent_analyzer import AgentOntologyAnalyzer

# By default, uses property-specific background files
analyzer = AgentOntologyAnalyzer(model="gemini")
result = analyzer.analyze("Student", description="A person enrolled in a university")

print(result)
# {
#   "properties": {
#     "rigidity": "~R",
#     "identity": "+I",
#     "own_identity": "-O",
#     "unity": "+U",
#     "dependence": "+D"
#   },
#   "reasoning": {
#     "rigidity": "Student is anti-rigid because...",
#     "identity": "Carries identity inherited from Person...",
#     ...
#   },
#   "classification": "Role (Anti-rigid, dependent)"
# }
```

### Without Any Background Files

```python
# Disable default backgrounds to use only built-in prompts
analyzer = AgentOntologyAnalyzer(model="gemini", use_default_backgrounds=False)
result = analyzer.analyze("Employee", description="Person working for organization")
```

### With Default Background File

Use the same background file for all property agents:

```python
analyzer = AgentOntologyAnalyzer(
    model="anthropic",
    default_background_file="resources/guarino_paper.txt"
)
result = analyzer.analyze("Employee", description="Person working for organization")
```

### With Property-Specific Background Files

Provide different background files for different properties:

```python
analyzer = AgentOntologyAnalyzer(
    model="gemini",
    background_files={
        "rigidity": "resources/rigidity_guide.txt",
        "identity": "resources/identity_guide.txt",
        "unity": "resources/unity_guide.txt",
        "dependence": "resources/dependence_guide.txt",
        "own_identity": "resources/own_identity_guide.txt"
    }
)
result = analyzer.analyze("Hotel", description="Building providing lodging")
```

### Hybrid Approach

Use a default background for most properties, but override specific ones:

```python
analyzer = AgentOntologyAnalyzer(
    model="anthropic",
    default_background_file="resources/guarino_paper.txt",
    background_files={
        "rigidity": "resources/specialized_rigidity_guide.txt"
        # Other properties will use default_background_file
    }
)
```

## Command-Line Usage

### Single Entity Analysis

```bash
# Basic usage (uses property-specific default backgrounds)
python scripts/analyze_entity_agents.py "Student" --desc "Person enrolled in university"

# Without any backgrounds
python scripts/analyze_entity_agents.py "Student" \
  --desc "Person enrolled in university" \
  --no-default-backgrounds

# With custom default background for all properties (overrides defaults)
python scripts/analyze_entity_agents.py "Student" \
  --desc "Person enrolled in university" \
  --default-background resources/custom_guarino_paper.txt \
  --model anthropic

# With property-specific backgrounds
python scripts/analyze_entity_agents.py "Employee" \
  --desc "Person working for organization" \
  --rigidity-background resources/rigidity_guide.txt \
  --identity-background resources/identity_guide.txt \
  --unity-background resources/unity_guide.txt \
  --verbose

# Save output to file
python scripts/analyze_entity_agents.py "Hotel" \
  --desc "Building providing lodging" \
  --default-background resources/guarino_paper.txt \
  --output hotel_analysis.json
```

### Batch OWL File Analysis

```bash
# Basic batch analysis (uses property-specific default backgrounds)
python scripts/batch_analyze_owl_agents.py ontology/test.owl --output results.tsv

# Without any backgrounds
python scripts/batch_analyze_owl_agents.py ontology/test.owl \
  --no-default-backgrounds \
  --output results.tsv

# With custom default background (overrides property-specific defaults)
python scripts/batch_analyze_owl_agents.py ontology/test.owl \
  --default-background resources/custom_paper.txt \
  --output results.tsv \
  --model anthropic

# With property-specific backgrounds
python scripts/batch_analyze_owl_agents.py ontology/test.owl \
  --rigidity-background resources/rigidity_guide.txt \
  --identity-background resources/identity_guide.txt \
  --unity-background resources/unity_guide.txt \
  --dependence-background resources/dependence_guide.txt \
  --format json \
  --output results.json

# Test on limited set
python scripts/batch_analyze_owl_agents.py ontology/large.owl \
  --limit 5 \
  --default-background resources/guarino_paper.txt \
  --output test_results.tsv
```

## Comparison: Standard vs Agent-Based

| Feature | OntologyAnalyzer | AgentOntologyAnalyzer |
|---------|------------------|----------------------|
| Analysis approach | Single LLM call for all properties | Separate LLM call per property |
| Background files | One file for all properties | Different file per property |
| Reasoning detail | Combined reasoning | Per-property reasoning |
| Cost | 1 API call per entity | 5 API calls per entity |
| Specialization | General analysis | Property-focused analysis |
| Use case | Fast batch processing | Detailed analysis, A/B testing |

## When to Use Agent-Based Approach

Use `AgentOntologyAnalyzer` when:

1. **Testing different background materials**: Compare how different papers/guides affect analysis of specific properties
2. **Detailed reasoning needed**: You want to see the reasoning for each property separately
3. **Property-specific expertise**: You have specialized guides for individual meta-properties
4. **Research experiments**: A/B testing different prompts or backgrounds
5. **Quality over speed**: Willing to make 5× API calls for more focused analysis

Use standard `OntologyAnalyzer` when:

1. **Batch processing**: Analyzing large numbers of entities efficiently
2. **Cost-sensitive**: Need to minimize API calls
3. **General analysis**: No property-specific background materials
4. **Quick results**: Single analysis per entity is sufficient

## Output Format

```json
{
  "properties": {
    "rigidity": "+R" | "-R" | "~R",
    "identity": "+I" | "-I",
    "own_identity": "+O" | "-O",
    "unity": "+U" | "-U" | "~U",
    "dependence": "+D" | "-D"
  },
  "reasoning": {
    "rigidity": "Explanation for rigidity value...",
    "identity": "Explanation for identity value...",
    "own_identity": "Explanation for own identity value...",
    "unity": "Explanation for unity value...",
    "dependence": "Explanation for dependence value..."
  },
  "classification": "Sortal/Role/Mixin/etc based on property combination"
}
```

## Testing

Run the test suite to see examples:

```bash
cd ontology_tools
python test_agent_analyzer.py
```

This will run 4 tests:
1. Analysis without background files
2. Analysis with default background file
3. Analysis with property-specific backgrounds
4. Comparison of results with/without backgrounds

## Property-Specific Prompts

Each agent has a specialized prompt focused on its meta-property:

- **Rigidity Agent**: Focuses on whether the property is essential to all instances
- **Identity Agent**: Focuses on whether the property carries an identity condition
- **Own Identity Agent**: Focuses on whether the property supplies its own IC (includes constraint checking)
- **Unity Agent**: Focuses on whether instances are integrated wholes
- **Dependence Agent**: Focuses on whether instances depend on other entities

## Advanced: Creating Property-Specific Background Files

When creating background files for specific properties, focus on:

### rigidity_guide.txt
- Detailed examples of rigid, non-rigid, and anti-rigid properties
- Modal logic considerations
- Essential vs accidental properties
- Roles and phases

### identity_guide.txt
- Identity conditions (ICs)
- Criteria for distinguishing instances
- Persistence conditions
- Sortal vs non-sortal properties

### own_identity_guide.txt
- Difference between carrying and supplying IC
- Inheritance of identity conditions
- Examples of properties with own IC vs inherited IC
- The +O → +I constraint

### unity_guide.txt
- Mereological structure
- Wholes vs aggregates
- Functional integration
- Scattered objects

### dependence_guide.txt
- Generic vs specific dependence
- Ontological dependence
- Examples of dependent entities (roles, qualities)
- Independent vs dependent properties

## Example Background Files Structure

```
resources/
├── guarino_paper.txt           # Default for all properties
└── property_guides/
    ├── rigidity_guide.txt      # Specialized for rigidity
    ├── identity_guide.txt      # Specialized for identity
    ├── own_identity_guide.txt  # Specialized for own identity
    ├── unity_guide.txt         # Specialized for unity
    └── dependence_guide.txt    # Specialized for dependence
```

## Notes

1. **Default Backgrounds**: By default, the analyzer loads property-specific excerpts from Guarino & Welty (2000). Use `--no-default-backgrounds` to disable this behavior.
2. **API Costs**: Agent-based analysis makes 5 API calls per entity vs 1 for standard analysis
3. **Performance**: Takes ~5× longer than standard analysis
4. **Consistency**: Each agent sees only its specialized prompt, which may improve focus but requires more API calls
5. **Constraint Checking**: The Own Identity agent receives the Identity result to enforce the +O → +I constraint
6. **Background File Size**: Files are automatically truncated to 50,000 characters to avoid context issues
7. **File Loading**: If default background files are not found, the analyzer will print warnings but continue with built-in prompts
