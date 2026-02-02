# Ontological Datasets

This directory contains datasets generated to stress-test ontology classification algorithms using the OntoClean methodology.

## Datasets

### 1. `ontological_stress_test.json` (Baseline)
*   **Model:** `google/gemini-2.5-flash`
*   **Size:** 10 domains x 15 terms.
*   **Focus:** General stress testing with mixed traps.

### 2. `ontological_stress_test_specific.json` (Specific Domains)
*   **Model:** `google/gemini-2.5-flash`
*   **Domains:** Treatment of bronchitis, Cycling, High-Frequency Trading, Myrmecology, Urban Parkour.
*   **Focus:** User-requested domains.

### 3. `large_taxonomy_dataset.json` (Deep Hierarchies)
*   **Model:** `google/gemini-2.5-flash`
*   **Size:** 2 domains x 40 terms.
*   **Domains:** eCommerce, Naval Warfare.
*   **Structure:** Explicitly engineered "Taxonomic Cores" (depth 3-5) mixed with "Ontological Traps" (Parts, Roles, Materials).
*   **Goal:** To test the ability to reconstruct deep trees while filtering out false positives.

## Generation Scripts

### `scripts/generate_test_dataset.py`
Generates the terms and ground-truth properties.
```bash
uv run --with requests --with python-dotenv --with tqdm scripts/generate_test_dataset.py <output.json> --num-terms 40
```

### `experiment/generate_taxonomy.py`
Attempts to reconstruct the taxonomy from the flat term list using an LLM.
```bash
uv run --with requests --with python-dotenv --with tqdm experiment/generate_taxonomy.py <input.json> <output.json>
```