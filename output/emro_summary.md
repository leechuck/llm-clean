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

## Takeaway

Under the current pipeline, EMRO appears largely OntoClean-consistent: the violations surfaced by the predictor are overwhelmingly traceable to a few systematic mislabelings of process-typed parent classes, not to genuine ontological flaws in EMRO. Improving meta-property prediction for upstream GO/BFO process terms should eliminate most of the reported violations.
