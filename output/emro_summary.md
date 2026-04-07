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

## The residual non-cascade verdicts (1 ONTOLOGY_ISSUE + 2 DONT_KNOW)

After excluding cascades and clear model errors, only three rows remain. They collapse to **two upstream decisions**.

### ONTOLOGY_ISSUE (1) — R2: `sweat secretion` ⊂ `secretion by tissue`

- URIs: GO:0160269 ⊂ GO:0032941
- Sub `sweat secretion` predicted **+R** (Property): *"The regulated release of sweat from the sweat glands."*
- Sup `secretion by tissue` predicted **−R** (Role): *"The controlled release of a substance by a tissue."*
- Constraint **R2**: a rigid class cannot have a non-rigid superclass — instances of a rigid kind must remain that kind in every world, so the parent cannot be more contingent than the child.
- Reviewer reasoning: the subsumption is genuine in GO (sweat secretion really is secretion by tissue), so the conflict is structural. Either the hierarchy is wrong, or one of the rigidity labels is wrong (most plausibly `secretion by tissue` should also be +R, since both terms denote biological process kinds rather than roles).
- Confidence: MEDIUM. This is the only violation flagged as a real ontology defect, but it is really a borderline labelling call about whether GO process classes are rigid kinds or roles — a tension that recurs throughout this dataset.

**Impact if the −R label on `secretion by tissue` is wrong (most likely case):** none on EMRO's instance data — the rigidity meta-property is not asserted in OWL, so no false subsumptions or instantiations follow. The damage is downstream of OntoClean itself: the term would be misclassified as a Role, which (a) invites modellers to attach it to bearers via role-playing patterns rather than as a natural kind, (b) suggests instances can stop being secretions-by-tissue while persisting (anti-rigidity), which is false, and (c) propagates the same error to every subclass, manufacturing further R2/I1 violations down the tree.

**Impact if the hierarchy is wrong instead:** an instance of `sweat secretion` would be entailed (via `rdfs:subClassOf`) to be a `secretion by tissue` in every world it exists — a *true* entailment that nevertheless sits under a parent the modeller has declared non-rigid, producing a logical inconsistency between the asserted taxonomy and the intended modal semantics. Reasoners won't flag it (OWL has no rigidity operator) but any downstream tool that respects OntoClean tags would derive contradictory modal commitments.

### DONT_KNOW (2) — U1: two children of `phenomenal cognitive experience`

Same parent, two children, same root cause:

| Child | URI | Predicted Unity |
|---|---|---|
| `emotional experience (feeling)` | EMRO:0000002 | **−U** |
| `sensory experience` | EMRO:0000005 | **~U** (anti-unity) |

- Parent `phenomenal cognitive experience` (EMRO:0000001) predicted **+U** (Property): *"A cognitive process during which an organism is aware of something either internal or external to itself."*
- Constraint **U1**: unity is inherited downward — a +U parent forces its subclasses to be +U. Here the parent is +U but the children are −U and ~U.
- Reviewer reasoning: the verdict hinges on a philosophically contested question — whether phenomenal/cognitive experiences are *intrinsic wholes*. Either the parent is wrongly +U (and the children are fine) or the children are wrongly −U/~U (and the parent is fine). The reviewer refuses to pick a side, so both rows are held as DONT_KNOW at MEDIUM confidence. Resolving the single meta-property on the parent would clear both violations.

**Impact if the parent is wrongly +U (experiences are not intrinsic wholes):** the ontology would assert that every awareness episode has determinate parts forming a single whole. Concrete consequences:
- *False instantiation*: any reasoner or annotation pipeline that uses unity as a guide for individuating instances would treat each phenomenal experience as one countable individual, so two simultaneous awarenesses (e.g. seeing red and feeling warm at once) would be wrongly forced into a single instance — or wrongly split, depending on the pipeline's bias.
- *False inferences about parts*: mereological queries ("what are the parts of this experience?") would be assumed to have well-defined answers, licensing part-whole entailments that the underlying phenomenology does not support.
- *Cascading +U on subclasses*: every subtype of cognition inherits the bogus unity criterion, polluting the entire cognitive branch of EMRO with the same individuation error.

**Impact if the children are wrongly −U/~U (the parent really is +U):** then `emotional experience` and `sensory experience` would deny that their instances are wholes despite being subtypes of something whose instances *are* wholes. Concrete consequences:
- *Lost entailments*: instance-level reasoning would fail to conclude that a particular feeling or sensory episode is an individuable whole, blocking legitimate counting, identity, and persistence inferences for affective and perceptual data.
- *False non-instantiation under aggregation*: anti-unity (~U) on `sensory experience` actively asserts that sensory episodes are mere aggregates with no intrinsic boundary, which would license a reasoner / curator to merge or split sensory-experience instances arbitrarily — corrupting any annotation that depends on episode identity (e.g., linking a single sensory event to a stimulus and a behavioural response).
- *Broken alignment with upper ontologies*: BFO/DOLCE-aligned tools that rely on unity to map cognitive processes to occurrent or quality categories would route these subclasses inconsistently with their parent, breaking cross-ontology mappings.

### Summary of residual impact

In every case the OntoClean labels are **not asserted in OWL**, so no OWL reasoner will derive a contradiction. The real impact is on:
1. *Instance individuation* — pipelines that count, merge, or split instances based on unity will systematically miscount affective and perceptual episodes;
2. *Modelling guidance* — wrong rigidity tags steer curators toward role-modelling patterns for what should be natural kinds, distorting all future extensions;
3. *Cross-ontology alignment* — mappings to BFO/DOLCE/UFO that respect meta-properties will route the affected classes inconsistently with their parents or children, producing silent data-integration errors rather than reasoner-visible inconsistencies.

## BFO-augmented prompt experiment

To test the diagnosis above (most violations are downstream of the model not knowing BFO's occurrent identity rule), the same finetuned model (`qwen7b-ontoclean`, IBEX `/ibex/scratch/projects/c2014/rob/ontoclean/models/qwen7b-ontoclean/merged`) was re-run on the same 64 EMRO entities with a **modified system prompt only** — no retraining. The new prompt adds:

- a CONTINUANT vs OCCURRENT distinction
- a critical rule that occurrents (BFO process / GO biological_process / event-describing classes) default to **−I, −O, ~U, +D**, only deviating if the definition explicitly states an identity criterion or whole-making principle
- continuant cheat-sheet for sortals / roles / qualities / mixins
- 5 worked examples (3 occurrents incl. `secretion by tissue` and `cognition`, 2 continuants)

Inference run: IBEX job 46419512, GTX 1080 Ti, ~3 h wall time. Outputs:
- `output/emro_ontoclean_predictions_bfo.tsv`
- `output/emro_ontoclean_violations_bfo.tsv`

### Headline numbers

| Metric | Baseline | BFO prompt | Δ |
|---|---|---|---|
| **Total violations** | 303 | **72** | **−76 %** |
| I1 (identity) | 135 | 27 | −80 % |
| U1 (unity) | 84 | 27 | −68 % |
| U2 (anti-unity) | 67 | 18 | −73 % |
| R2 (rigidity) | 17 | **0** | **−100 %** |
| O1 warnings | — | 2 | new |
| Predictions changed | — | **64 / 64** | every entity flipped |

### Classification distribution shift

| Classification | Baseline | BFO |
|---|---|---|
| Process | 4 | **53** |
| Quality | 1 | 7 |
| Sortal | 0 | 3 |
| Mixin | 14 | 1 |
| Role | **40** | 0 |
| Property | 2 | 0 |
| Process Quality / Biological Process / Characteristic | 3 | 0 |

The baseline model treated EMRO's mostly-process content as continuant Roles played by bearers; the BFO-prompted run correctly recognises EMRO as a process ontology.

### Anatomy of the 72 remaining violations (+ 2 warnings) — the same cascade pattern as baseline, just much smaller

Just as in the baseline analysis, the residual violations are **not 74 independent errors** — they all trace back to the same kind of root-cascade structure, but the number of root errors has collapsed from "many GO/BFO process classes" down to **exactly 4 mislabeled classes**:

| # rows | Constraint(s) | Root mislabeling | What the model got wrong |
|---:|---|---|---|
| **44** | 21 × I1, 21 × U1, 2 × O1 | **`system process`** predicted as Process but with `+I, +O, +U` instead of `−I, −O, ~U` | The classification label is right (Process) but the meta-property values still treat it as a continuant kind. Every subclass of `system process` is correctly `−I` and `~U`, so neither `+I` nor `+U` propagates downward — generating one I1 and one U1 per descendant pair, plus two O1 warnings where descendants are also `+O`. |
| **12** | 6 × I1, 6 × U1 | **`regulation of biological quality`** predicted as a continuant **Sortal** (`+R, +I, +O, +U, −D`) | Should be a Process (regulatory occurrent). Same cascade: every descendant is a `−I, ~U` process, so `+I` and `+U` fail to inherit, producing 6 I1 + 6 U1. |
| **12** | 12 × U2 | **`emotional experience (feeling)`** and **`sensory experience`** each predicted as Sortals (`+U`) | Both sit under the chain `phenomenal cognitive experience → cognition → nervous system process → multicellular organismal process → biological_process → process`, every link of which is correctly `~U`. A single `+U` child therefore violates U2 against **every** `~U` ancestor in the chain — producing 6 U2 per child = 12 U2 in total. |
| **6** | 6 × U2 | The same `+U` mislabeling on `system process` (3 rows) and on `regulation of biological quality` (3 rows) | Each is `+U` while sitting under `~U` process ancestors, generating one U2 per ancestor in their respective subsumption chains. |

**Sum: 44 + 12 + 12 + 6 = 74. Every single violation/warning attributed.**

### How the residual errors relate to each other

There are really just **two failure modes** behind the four root errors:

1. **`system process` and `regulation of biological quality` are still being treated as continuants on the meta-property axis even when classified as Process.** The BFO prompt fixed the classification label but not all the property assignments for these two specific terms. They sit at an awkward boundary in EMRO's hierarchy — both are descendants of `process` but their definitions read like "regulatory function" and "system function", which the model still pattern-matches to "thing that has a function" (a sortal/role bearer) rather than to "the regulating event itself".

2. **`emotional experience (feeling)` and `sensory experience` are being treated as continuant sortals**, not as the phenomenal events their parent (`phenomenal cognitive experience`, now correctly Process ~U) marks them as. This was already the source of the 2 DONT_KNOW rows in the baseline review, and it remains the only philosophically-genuinely-hard part of EMRO: are subjective experiences events or substantial bearers? The BFO prompt didn't resolve this because the prompt does not directly tell the model how to handle phenomenal terms — only how to handle BFO occurrents and GO processes.

### Comparison to the baseline residue

| Aspect | Baseline | BFO prompt |
|---|---|---|
| Root mislabelings driving cascades | many process classes (GO/BFO occurrents over-assigned `+I`) | **4 specific classes** |
| Cascading rows | 253 (`CASCADES_FROM_DIRECT`) | **74 (every row attributable)** |
| Real ontology defects flagged | 1 (the GO `sweat secretion` R2) | **0** — the R2 is gone |
| Philosophically open cases | 2 (DONT_KNOW on phenomenal cognitive experience) | **2** (still emotional/sensory experience as continuant vs occurrent) |
| Total violations | 303 | 72 |

### What would close the rest

Eliminating the four root errors would, by the cascade math above, reduce the violation count from 74 → 0. Two cheap interventions could plausibly do it:

1. **Strengthen the BFO rule for "system X" and "regulation of X" patterns.** The current prompt's occurrent rule fires reliably on classes whose definitions describe events ("release of", "controlled X by Y", "process during which") but is less robust on classes whose definitions describe a *capacity* or *function* — `system process` and `regulation of biological quality` slip through. Adding one sentence of the form *"GO classes whose names begin with 'regulation of' or end in 'system process' are still occurrents and inherit the −I, −O, ~U, +D defaults"* would likely capture both root errors.

2. **Add a phenomenal-event rule.** A second one-liner *"Phenomenal experiences (feelings, perceptions, sensations) are subjective occurrents — not substantial sortals — and inherit the same occurrent defaults as their parent class"* should flip `emotional experience` and `sensory experience` from Sortal to Process and eliminate the U2 + O1 cluster.

A second prompt iteration with these two additions is the obvious next step before any retraining.

## Takeaway

Under the current pipeline, EMRO appears largely OntoClean-consistent: the violations surfaced by the predictor are overwhelmingly traceable to a few systematic mislabelings of process-typed parent classes, not to genuine ontological flaws in EMRO. The BFO-augmented prompt experiment empirically confirms this — a single prompt change (no retraining) reduced violations from 303 to 72 (−76 %), eliminated the only ONTOLOGY_ISSUE, and collapsed the residue down to 4 specific root mislabelings whose cascades fully account for every remaining row. The two philosophically contested cases from the baseline (status of phenomenal experiences) remain the hardest part of the analysis, as expected.
