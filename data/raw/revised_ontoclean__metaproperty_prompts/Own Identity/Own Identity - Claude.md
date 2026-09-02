# Claude Opus 5 (2026-09-01)

## Headline problem: the stated constraint is missing its load-bearing half

Your prompt says `+O → +I`. That's correct but incomplete. The source definition has three clauses, and the first one is rigidity:

> **Definition 6.** A property $\varphi$ supplies an IC $\Gamma$ iff **i) it is rigid**; ii) it carries $\Gamma$; and iii) $\Gamma$ is not carried by all the properties subsuming $\varphi$.
> […] From the above definitions, it is obvious that **+O implies +I and +R**.
> — Guarino & Welty, *A Formal Ontology of Properties* (2000)

So the constraint you need is `+O → +I ∧ +R`. Non-rigid properties are **debarred from supplying identity**, full stop. This is not a detail — it is the reason O was introduced. The literature's own worked case is exactly the one your prompt will get wrong:

> it seems that non-rigid properties like STUDENT can only carry their ICs, inheriting those supplied by their subsuming rigid properties like PERSON. […] an IC allegedly supplied by STUDENT (say, having the same registration number) may be only **local**, within a certain studenthood experience.

An agent given your current prompt will find a registration number, matriculation ID, or enrolment record, conclude that *Student* supplies a criterion, and mark it `+O`. Your example list says `−O`, so the agent receives a rule and a counterexample to that rule and will resolve the tension inconsistently across classes.

Three further issues:

**1. "Global" is unexplained, and it is carrying the whole argument.** *Global* contrasts with *local*: a local IC settles identity only among things currently falling under the property; a global one settles it whenever the entity exists. Welty's own formulation annotates the global version "**rigid properties only**." An agent reading "global" without this will parse it as "important" or "universal" and the word will do no work.

**2. Clause (iii) is missing, and it is not "has no +I ancestor."** The actual test is whether the IC is carried by *all* subsuming properties. If a class introduces a *new, compatible* criterion on top of an inherited one, it is `+O` — the paper is explicit that inheriting different-but-compatible ICs from multiple parents still counts as supplying. Your *Person* / *Physical Object* pair is only coherent under this reading, and the prompt never states it.

**3. `−O` bundles three cases that behave differently.** Your examples cover "inherits it" (*Student*) and "has none" (*Red*), and the rigidity gate adds a third. These need different reason codes — see below.

---

## Suggested rewrite

> You are an expert Ontological Analyst specializing in the Own Identity meta-property from Guarino and Welty (2000).
>
> **Own Identity (O) — Supplies an Identity Condition**
>
> Carrying identity (+I) means the class has an answer to "same one or different one?" Supplying identity (+O) means the class is **where that answer originates**. Most classes with an answer inherited it from further up; only some introduce one.
>
> The criterion must be **global**: valid whenever the instance exists, not merely while it happens to fall under this class. A criterion that only works during an episode — a registration number that tracks someone while enrolled and stops afterwards — is a *local* criterion and does not count.
>
> Only **rigid** classes can supply identity. This follows from globality: a criterion that must hold throughout an instance's existence can only come from a class the instance belongs to throughout its existence. A class its instances can enter and leave cannot be the source.
>
> **+O — supplies identity.** Requires all three: the class is rigid (+R), it carries an IC (+I), and it introduces a criterion that at least one of its parents lacks.
>
> - *Person* — introduces personal-identity criteria that no more general class provides.
> - *Amount of Matter* — same constituent matter, same amount. Its own criterion, owed to nothing above it.
> - *Statue* — sameness of form. Note this conflicts with the criterion for *Amount of Clay*; both are +O, which is precisely why they must be kept apart.
> - *Organism*, *Event*, *Number*, *Set*
>
> **−O — does not supply identity.** Record which of the three reasons applies.
>
> - **Not rigid** — *Student*, *Employee*, *Passenger*, *Adult*. These may look as though they bring a criterion (student number, employee ID, ticket number). Those criteria are local: they cease to track the individual once the role or phase ends. Identity is inherited from *Person*.
> - **Rigid, but adds nothing** — *Mammal* under *Organism*; *Integer* under *Number*. Genuinely rigid, genuinely +I, but the criterion is entirely the parent's. Being a mammal contributes no new answer to "same one?" beyond being an organism.
> - **Carries no IC at all** — *Red*, *Entity*, *Large*. −I, therefore −O trivially.

---

## The decision procedure to give the agent

Three gates, then one judgment. The first three are lookups; only the fourth requires reasoning.

**Gate 1 — Identity.** Is the class `+I`? If no → `−O (non-sortal)`. Stop.

**Gate 2 — Rigidity.** Is the class `+R`? If it is `−R` or `~R` → `−O (not rigid)`. Stop. Do not proceed on the strength of an apparent criterion; see the globality test below.

**Gate 3 — Parents.** Retrieve every subsuming class and the IC each one carries. If the class has no parent carrying an IC → `+O`.

**Judgment — Augmentation.** The class inherits criterion $\Gamma_{\text{parent}}$. Ask: does being *this* kind of thing add a further answer to "same one or different one?" that the parent does not already give?

- Adds nothing → `−O (inherited)`
- Adds a compatible further criterion → `+O (augments)`
- Appears to need an *incompatible* criterion → **report a violation.** ICs can be augmented but never overridden. A subclass requiring a criterion that contradicts its parent's means the subsumption is wrong, not that the label is interesting. This is the most valuable output of the whole O analysis.

**Globality test, for use inside Gate 2 when a criterion looks compelling.** Take the candidate criterion and apply it at a time when the individual is *not* an instance of the class. Does it still track them?

- *Employee number*, applied after they leave: no longer identifies that person. **Local** → not an IC for O purposes.
- *Person*'s criterion, applied at any point in that person's life: still holds. **Global.**

The equivalent framing, which agents find easier: *a criterion that can outlive its own applicability is local.*

<details>
<summary><strong>Why O is different from every other metaproperty in the set — and what follows for your pipeline</strong></summary>

Identity, unity, rigidity, and dependence are properties of a class considered by itself. You can judge them from a name and a description.

**O cannot be judged that way.** It is a property of a class *plus its position in the taxonomy*. The same class flips label depending on what sits above it:

- *Person* directly under *Entity* (−I) → `+O`
- *Person* under *Organism* (+O, biological continuity), adding nothing further → `−O (inherited)`
- *Person* under *Organism*, adding psychological continuity → `+O (augments)`

Three consequences:

1. **The agent must be given ancestors and their ICs.** A per-class prompt with only name and description cannot produce a correct O label. If your current harness feeds one class at a time, O is the metaproperty that breaks.
2. **O labels are invalidated by hierarchy edits.** Reparenting a class changes the O labels of it and its descendants. Cache accordingly, or recompute.
3. **O should be computed last.** It consumes I and R. If the O classifier re-derives rigidity internally rather than reading the R label, you will get classes marked `~R` by one prompt and `+O` by another — a contradiction your validator should catch, but better not to generate.
</details>

<details>
<summary><strong>The constraint that makes O worth computing</strong></summary>

I and R constrain subsumption on their own. O adds one thing the others cannot express: **two classes supplying incompatible ICs must be disjoint.** Neither may subsume the other, and no individual may instantiate both.

This is what finally separates the classic pairs:

- *Statue* (+O, sameness of form) and *Amount of Clay* (+O, sameness of matter). Squash the statue: same clay, different statue — so the criteria disagree, so these are two entities, not one.
- *Person* (+O) and *Amount of Matter* (+O). Same reasoning, and the reason constitution cannot be modelled as subsumption.

The useful analogy for an agent, which the paper itself uses: supplying an IC is like defining an equality method on a class — **except that subclasses may extend it and may never override it.** An ontology in which a subclass silently redefines what sameness means is broken in the same way a subclass that violates the equality contract is broken.

Practical check to run over your labelled output: for each class, walk up to collect every `+O` ancestor. If two of them supply criteria that can disagree about a case, you have found a real modelling error.
</details>

<details>
<summary><strong>Common confusions to warn the agent against</strong></summary>

| Wrong reading | Correction |
|---|---|
| "It has its own ID field, so +O" | Student numbers, employee IDs, and order references are local criteria attached to episodes. Run the globality test. |
| "Its parent is +O, so it must be −O" | +O stacks. A rigid subclass adding a compatible criterion is +O under a +O parent. Clause (iii) says the IC must not be carried by *all* subsumers, not that no subsumer carries one. |
| "It's +I, so it's +O" | +I is one of three requirements. Most +I classes are −O. |
| "It's a role with a clear criterion, so +O" | Roles are non-rigid and therefore excluded regardless of how clear the criterion looks. |
| "It's rigid and +I, so +O" | Still needs to add something. *Mammal* fails on augmentation alone. |
| "I can't articulate its criterion, so −O" | Recognising that a class originates identity does not require stating the criterion. The paper is explicit that sortal/non-sortal discrimination is useful without knowing which IC is carried. |
| "The subclass needs a different criterion, so +O" | Only if *compatible*. Incompatible means the subsumption is wrong. Report it. |
| "It's at the top of the hierarchy, so +O" | Top-level classes are often −I (*Entity*, *Thing*) and therefore −O. Height does not imply supply. |
</details>

<details>
<summary><strong>Near-miss pairs for calibration</strong></summary>

- *Student* (−O, not rigid) vs. *Person* (+O). The pair the metaproperty exists to distinguish, and the one where the registration-number trap fires. Worth including verbatim in the prompt with the local-IC explanation attached.
- *Mammal* (−O, inherited) vs. *Organism* (+O). Rigid, +I, and still −O — isolates the augmentation clause from the rigidity gate.
- *Person* (+O) under *Physical Object* (+O). Legitimate stacked supply; blocks the "parent is +O so child is −O" inference.
- *Statue* (+O) vs. *Amount of Clay* (+O). Incompatible criteria, disjointness constraint fires.
- *Adult* (−O, ~R) vs. *Mammal* (−O, +R). Same label, different reason code — shows why the reason matters.
- *Amount of Matter* (+O, +I, ~U) vs. *Red* (−O, −I). The +O extreme against the trivial −O.
</details>

<details>
<summary><strong>Formal statement, if you want it in documentation</strong></summary>

Local versus global (Welty's formulation, with $t$ ranging over times):

$$\text{Local: } \quad \varphi(x,t) \wedge \varphi(y,t') \rightarrow \big(\Gamma(x,y,t,t') \leftrightarrow x = y\big)$$

$$\text{Global (rigid properties only): } \quad \varphi(x,t) \rightarrow \big(\varphi(y,t') \wedge \Gamma(x,y,t,t') \leftrightarrow x = y\big)$$

Then $\varphi$ **supplies** $\Gamma$ iff $\varphi$ is rigid, $\varphi$ carries $\Gamma$, and $\neg\forall \psi\,(\psi \sqsupseteq \varphi \rightarrow \psi \text{ carries } \Gamma)$.

`+O` iff some $\Gamma$ satisfies this; `−O` otherwise. Whence `+O → +I` and `+O → +R`.

The third clause is the one to read carefully: it is a negated universal, not "no subsumer carries $\Gamma$." That is what licenses multiple inheritance of compatible ICs to count as supply, and it is the clause your current prompt has no counterpart for.
</details>

---

## One structural suggestion

O is the metaproperty you should probably **not** be spending an LLM call on in the general case. Gates 1–3 are pure lookups against labels you already have plus the class graph; the only genuinely semantic step is the augmentation judgment, which arises for a minority of classes — those that are rigid, +I, and have a +I parent. Run the gates deterministically, and invoke the model only on survivors. You get lower cost, and more importantly you get *consistency*: a deterministic gate cannot mark a class `~R` in one prompt and `+O` in another.

The residual cases are worth inspecting by hand at first, because the interesting ones are not labelling problems at all — they are the incompatible-IC cases, which are hierarchy errors. That is the actual yield of the O analysis, and a classifier that only emits `+O`/`−O` will throw it away.

Note also the ordering dependency: O's rigidity gate consumes the R label, so the Rigidity prompt needs settling before this one can be trusted. Rigidity is still outstanding, and it is where the `−R`/`~R` collapse does the most damage — a class wrongly marked `−R` instead of `~R` disables the subsumption checks that constitute most of OntoClean's diagnostic value, and now also silently corrupts every O label beneath it.