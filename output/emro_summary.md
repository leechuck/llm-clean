# EMRO OntoClean Analysis — Summary

Summary of existing EMRO (Emotion Ontology) related results in this repository.

## Source

- Ontology: `ontology/emro.owl` (Emotion Ontology)
- Extraction script: `scripts/extract_emro_entities.groovy`

## Artifacts

| File | Rows | Description |
|---|---|---|
| `output/emro_entities.tsv` | 64 | Extracted classes: `uri, label, definition, parent_label` |
| `output/emro_ontoclean_predictions.tsv` | 64 | LLM predictions of Guarino & Welty meta-properties (rigidity, identity, own_identity, unity, dependence) plus a top-level classification and reasoning |
| `output/emro_ontoclean_violations.tsv` | 303 | Raw OntoClean constraint violations derived from the predictions, joining each subclass/superclass pair that breaks a constraint |
| `output/emro_ontoclean_violations_reviewed.tsv` | 303 | Same violations re-judged by an LLM reviewer with `verdict, confidence, reasoning` columns and an `is_direct` flag indicating whether the violation is a direct sub→super conflict or cascades from one |

## Predicted classifications (64 entities)

| Classification | Count |
|---|---|
| Role | 40 |
| Mixin | 14 |
| Process | 4 |
| Property | 2 |
| Quality | 1 |
| Process Quality | 1 |
| Characteristic | 1 |
| Biological Process | 1 |

The dominance of **Role** (≈63%) and **Mixin** (≈22%) reflects EMRO's heavy reuse of upstream GO/BFO process classes as parents, which the model treats as contextual / non-rigid kinds.

## Violations by constraint

| Constraint | Count | Meaning |
|---|---|---|
| I1 | 135 | Identity carried by a superclass not inherited by the subclass |
| U1 | 84 | Unity property of superclass not inherited |
| U2 | 67 | Anti-unity superclass with a unity-bearing subclass |
| R2 | 17 | Rigid subclass under a non-rigid / anti-rigid superclass |
| **Total** | **303** | |

## Reviewer verdicts

| Verdict | Count |
|---|---|
| CASCADES_FROM_DIRECT | 253 |
| MODEL_ERROR | 47 |
| DONT_KNOW | 2 |
| ONTOLOGY_ISSUE | 1 |

Reviewer confidence: **HIGH** on 275, **MEDIUM** on 28.

## Interpretation

- Only **1 of 303** violations was attributed to an actual problem in EMRO itself; the remaining 302 are explained as artifacts of the meta-property prediction step.
- **83%** of violations (`CASCADES_FROM_DIRECT`) propagate from a small number of root mislabelings rather than being independent errors.
- The dominant root cause identified by the reviewer is the model **over-assigning `+I` (identity) to GO/BFO process classes**. Processes generally do not supply identity conditions for their subtypes (identity comes from the bearer), so any `+I` on a process parent automatically generates I1 violations for every `-I` subclass beneath it, accounting for the large I1 count and most of the cascades.
- The U1/U2 cluster has a similar flavour: process-like parents are inconsistently labelled for unity, producing structural violations that the reviewer attributes to model error rather than ontology defects.

## Takeaway

Under the current pipeline, EMRO appears largely OntoClean-consistent: the violations surfaced by the predictor are overwhelmingly traceable to a few systematic mislabelings of process-typed parent classes, not to genuine ontological flaws in EMRO. Improving meta-property prediction for upstream GO/BFO process terms should eliminate most of the reported violations.
