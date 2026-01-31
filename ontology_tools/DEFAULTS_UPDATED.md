# Default Background Files Updated

## Summary

The `AgentOntologyAnalyzer` has been updated to automatically load property-specific background files by default. This provides better, more focused analysis for each ontological meta-property without requiring users to specify background files manually.

## Default Background Files

The following property-specific files are loaded by default:

| Property | Default File Path |
|----------|------------------|
| Rigidity | `resources/converted_text_files/guarino_text_files/01-guarino00formal-rigidity.txt` |
| Identity | `resources/converted_text_files/guarino_text_files/01-guarino00formal-identity.txt` |
| Own Identity | `resources/converted_text_files/guarino_text_files/01-guarino00formal-identity.txt` |
| Unity | `resources/converted_text_files/guarino_text_files/01-guarino00formal-unity.txt` |
| Dependence | `resources/converted_text_files/guarino_text_files/01-guarino00formal-dependence.txt` |

## Behavior

### Default Behavior (NEW)
When you create an analyzer without specifying backgrounds, it **automatically loads** the property-specific files above:

```python
from ontology_tools.agent_analyzer import AgentOntologyAnalyzer

# This now loads property-specific backgrounds by default
analyzer = AgentOntologyAnalyzer(model="gemini")
```

Output when initializing:
```
Loading default property-specific background files...
  ✓ Loaded rigidity: resources/converted_text_files/guarino_text_files/01-guarino00formal-rigidity.txt
  ✓ Loaded identity: resources/converted_text_files/guarino_text_files/01-guarino00formal-identity.txt
  ✓ Loaded own_identity: resources/converted_text_files/guarino_text_files/01-guarino00formal-identity.txt
  ✓ Loaded unity: resources/converted_text_files/guarino_text_files/01-guarino00formal-unity.txt
  ✓ Loaded dependence: resources/converted_text_files/guarino_text_files/01-guarino00formal-dependence.txt
```

### Disabling Defaults
To use **no background files** (only built-in prompts):

```python
analyzer = AgentOntologyAnalyzer(model="gemini", use_default_backgrounds=False)
```

Or via command line:
```bash
python scripts/analyze_entity_agents.py "Student" \
  --desc "Person enrolled in university" \
  --no-default-backgrounds
```

### Overriding Defaults
You can override specific properties while keeping defaults for others:

```python
analyzer = AgentOntologyAnalyzer(
    model="gemini",
    background_files={
        "rigidity": "my_custom_rigidity_guide.txt"
        # identity, own_identity, unity, dependence will use defaults
    }
)
```

### Using Single Background for All
To use **one background file for all properties** (overrides defaults):

```python
analyzer = AgentOntologyAnalyzer(
    model="gemini",
    default_background_file="resources/complete_guarino_paper.txt"
)
```

Or via command line:
```bash
python scripts/analyze_entity_agents.py "Student" \
  --default-background resources/complete_guarino_paper.txt
```

## Priority Order

The analyzer loads backgrounds in this priority order (later overrides earlier):

1. **Default property-specific files** (if `use_default_backgrounds=True`)
2. **Single default background** (if `default_background_file` is provided)
3. **Custom property-specific files** (if `background_files` dict is provided)

## Files Modified

All files have been updated to support this new behavior:

### Core Library
- `agent_analyzer.py` - Added DEFAULT_BACKGROUND_FILES constant and loading logic

### Scripts
- `analyze_entity_agents.py` - Added `--no-default-backgrounds` flag
- `batch_analyze_owl_agents.py` - Added `--no-default-backgrounds` flag
- `compare_analyzers.py` - Added `--no-default-backgrounds` flag

### Tests & Documentation
- `test_agent_analyzer.py` - Added test for default backgrounds
- `AGENT_ANALYZER_README.md` - Updated documentation with defaults section

## Migration Notes

**Backward Compatibility**: Existing code will continue to work but will now load property-specific backgrounds by default. If you want the old behavior (no backgrounds), explicitly set `use_default_backgrounds=False`.

**File Warnings**: If the default files are not found at the specified paths, the analyzer will print warnings but continue using built-in prompts for those properties.

## Testing

Run the test suite to see the defaults in action:

```bash
cd ontology_tools
python test_agent_analyzer.py
```

This will run 5 tests including:
1. Analysis without backgrounds (use_default_backgrounds=False)
2. Analysis with property-specific defaults (new default behavior)
3. Analysis with single default background
4. Analysis with custom property-specific backgrounds
5. Comparison of results with/without backgrounds
