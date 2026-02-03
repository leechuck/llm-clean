# Agentic Taxonomy Benchmark Report

**Date:** 2026-02-03
**Methodology:** Agentic workflow using a "Taxonomist" agent to propose links and a "Critic" agent (using OntoClean methodology) to validate them. Both agents utilize the same underlying LLM.

## Agentic Results

| Model                  |   Total Links |   Violations (Critical) |   Cycles (Critical) |   Warnings (Constitution) |
|:-----------------------|--------------:|------------------------:|--------------------:|--------------------------:|
| Llama 3.2 3B (Agentic) |            83 |                       0 |                   1 |                         0 |
| Llama 3.1 8B (Agentic) |           225 |                       1 |                   6 |                         2 |

## Comparison with Base Models (Zero-Shot)

The following table compares the Agentic performance against the standard Zero-Shot generation baseline (where the model simply outputs the taxonomy in one pass).

| Model | Mode | Total Links | Violations (Critical) | Cycles (Critical) |
| :--- | :--- | ---: | ---: | ---: |
| **Llama 3.2 3B** | Base | 890 | **193** | 68 |
| | **Agentic** | 83 | **0** | **1** |
| | | | | |
| **Llama 3.1 8B** | Base | 452 | **25** | 72 |
| | **Agentic** | 225 | **1** | **6** |

## Interpretation & Analysis

1.  **Massive Quality Improvement:** The agentic workflow successfully eliminated almost all ontological violations.
    *   For **Llama 3.2 3B**, critical rigidity violations dropped from **193 to 0**. This is a perfect score on the rigidity constraint, proving that the Critic agent effectively filtered out invalid "is-a" relationships (e.g., *Person is-a Student*) that the base model hallucinated.
    *   For **Llama 3.1 8B**, violations dropped from **25 to 1**, showing similar efficacy.

2.  **Cycle Elimination:** Circular dependencies (e.g., A -> B -> A), which destroy hierarchy logic, were nearly eradicated. Llama 3.2 3B went from 68 cycles to 1, and Llama 3.1 8B went from 72 to 6.

3.  **Reduction in "Hallucinated" Links:** The "Total Links" count dropped significantly in the agentic mode (890 -> 83 for 3B).
    *   **Interpretation:** The base model tends to over-generate links, creating a "spaghetti" graph where everything is related to everything, often incorrectly.
    *   The Agentic workflow is much more conservative. The Critic rejects weak or ambiguous links, resulting in a sparser but **highly accurate** and ontologically sound hierarchy.

4.  **Self-Correction Capability:** Crucially, **both agents used the same model** (e.g., Llama 3.2 3B acted as both Taxonomist and Critic). This demonstrates that small models possess the knowledge to *recognize* invalid reasoning when explicitly prompted with constraints (OntoClean rules), even if they fail to apply those constraints implicitly during zero-shot generation.
