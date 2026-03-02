# Experiment Comparison: Gemini 2.5 Flash vs Llama 3.3 70B

**Date:** February 2, 2026
**Dataset:** `datasets/large_taxonomy_dataset.json` (eCommerce, Naval Warfare)

## Results

### Google Gemini 2.5 Flash
*   **Total Links:** 50 (19 eCommerce + 31 Naval Warfare)
*   **Violations:** 0 Critical
*   **Warnings:** 2 Constitution Traps
    *   `Missile` -> `Explosive` (Object subclass of Material)
    *   `Torpedo` -> `Explosive` (Object subclass of Material)
*   **Analysis:** Gemini generated a denser taxonomy but fell for the "Constitution Trap" where it classified weapons as subclasses of the material they contain/are made of.

### Meta Llama 3.3 70B
*   **Total Links:** 42 (18 eCommerce + 24 Naval Warfare)
*   **Violations:** 0 Critical
*   **Warnings:** 0
*   **Analysis:** Llama produced a slightly sparser taxonomy (fewer links) but avoided all ontological traps in this run. It was more conservative/precise regarding the "Is-A" relationship.

## Conclusion
For this specific strict ontology task, **Llama 3.3 70B** outperformed Gemini 2.5 Flash by avoiding the "Object IS-A Material" fallacy, albeit with slightly lower recall (connectivity).
