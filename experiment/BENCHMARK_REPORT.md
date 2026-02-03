# Benchmark Report: Ontology Taxonomy Generation

**Date:** 2026-02-03
**Dataset:** 10 Domains (35 terms each) including "Treatment of bronchitis", "Cycling", etc.
**Evaluation Criteria:** OntoClean Constraints (Rigidity, Constitution, Cycle Detection).

## Summary Table

| Model                 |   Total Links |   Violations (Critical) |   Cycles (Critical) |   Warnings (Constitution) |
|:----------------------|--------------:|------------------------:|--------------------:|--------------------------:|
| Gemini 2.5 Flash      |           291 |                       1 |                   0 |                         3 |
| Claude 3.5 Sonnet     |           211 |                       5 |                   0 |                         3 |
| GPT-4o                |           193 |                       0 |                   0 |                         1 |
| Llama 3.3 70B         |           218 |                       0 |                   0 |                         3 |
| Llama 3.2 3B          |           890 |                     193 |                  68 |                        72 |
| Mistral Large         |           223 |                       0 |                   0 |                         3 |
| Qwen 2.5 72B          |           217 |                       0 |                   0 |                         0 |
| DeepSeek V3           |           201 |                       0 |                   0 |                         2 |
| Llama 3.1 8B          |           452 |                      25 |                  72 |                        21 |
| Gemini 2.0 Flash Lite |           225 |                       1 |                   0 |                         5 |
| Gemini 2.5 Flash Lite |           279 |                       5 |                   0 |                         8 |
| Qwen 2.5 7B           |           375 |                      14 |                  31 |                         4 |
| Gemma 2 9B            |           261 |                       7 |                   2 |                         7 |

## Interpretation

*   **Total Links:** Higher is usually better (more connections found), provided they are correct.
*   **Violations (Critical):** Rigid Child is-a Anti-Rigid Parent. (e.g., Person is-a Student). MUST be 0.
*   **Cycles (Critical):** Circular dependencies. MUST be 0.
*   **Warnings:** Object is-a Material (e.g., Ring is-a Gold). Likely "Made-of" confusion. Should be low.

