# Claude Opus 5 (2026-09-01)

## Headline problem: the disjointness clause is missing, and without it nearly everything is +D

OntoClean's D is **external** dependence, and the formal definition carries an exclusion that your version drops: the entity depended upon must not be a **part**, a **constituent**, or a **member** of the instance. Remove that clause and the metaproperty collapses — a *Person* depends on their organs, a *Car* on its engine, a *Physical Object* on its matter, so every one of your −D examples flips to +D. An agent given this prompt will mark almost the entire ontology dependent. This is the single fix that matters most.

Four further issues:

**1. "Intrinsically depend" is backwards.** Dependence in OntoClean is definitionally *extrinsic*. Worse, intrinsic/extrinsic is a live and separate distinction in this literature (it does work in the rigidity discussion), so the word will pull the agent toward the wrong axis.

**2. "without depending on *specific* other entities" inverts the quantifier.** OntoClean uses **generic** dependence: there must exist *some* instance of the depended-upon class, not one particular individual. A student needs some institution, not that one. As written, an agent will reason "a student can transfer schools, therefore no specific dependence, therefore −D" — and get *Student* exactly wrong.

**3. *Parasite* teaches causal dependence instead of existential dependence.** The host is genuinely external and disjoint, so the label survives, but the example licenses a bad generalisation: a plant needs sunlight, an animal needs oxygen, every object needs spacetime. None of those are +D. Background causal preconditions are not external dependence, and *Parasite* is the example most likely to blur that line.

**4. No ~D exists — say so.** Having just given the agent two trichotomous metaproperties, you should state explicitly that dependence is a dichotomy. Otherwise it will invent `~D` by analogy on hard cases.

---

## Suggested rewrite

> You are an expert Ontological Analyst specializing in the Dependence meta-property from Guarino and Welty (2000).
>
> **Dependence (D) — External Dependence**
>
> A property is externally dependent when nothing can be an instance of it *all by itself*. Being that kind of thing requires some **other, separate** entity to exist alongside it.
>
> "Separate" is what makes this metaproperty non-trivial. The required entity must be **outside** the instance — not one of its parts, not the matter it is made of, not one of its members. Everything depends on its own parts; that is not what is being measured here. Nor does it count that instances need favourable background conditions such as air, gravity, or spacetime.
>
> The requirement is **generic**: some instance of the other class must exist. It need not be one particular individual, and the instance may be free to swap which one it stands in relation to.
>
> This metaproperty has only two values. There is no anti-dependence.
>
> **+D — externally dependent.** Every instance, necessarily, coexists with some separate entity of another kind. Usually you can see the dependence in the definition of the class: you cannot say what the class *is* without mentioning the other thing.
>
> - *Student* — needs some educational institution or teacher. Which one may change; that one exists cannot.
> - *Parent* — needs a child. The child is not part of the parent.
> - *Employee*, *Passenger*, *Tenant*, *Patient* — roles, each naming its counterpart.
> - *Hole* — needs a host object to be a hole in. Note this one is **+D and rigid**; dependence is not confined to roles.
> - *Surface*, *Boundary*, *Shadow* — dependent on what they bound or are cast by.
>
> **−D — not externally dependent.** An instance could exist in a world containing nothing else of relevance. It may well have parts, constituents, and members it could not survive without — that does not make it dependent.
>
> - *Person* — a person needs organs, but organs are parts.
> - *Apple*, *Rock*, *Physical Object*
> - *Team* — a team needs members, but members are members. Dependence excludes them, so *Team* is −D even though *Team Member* is +D.

---

## The decision procedure to give the agent

**Step 1 — Name the candidate.** Complete this sentence: "Nothing can be an X unless there is also some ______." If you cannot fill the blank, → **−D**.

**Step 2 — Run the disjointness filter.** Is the thing you named any of the following?

| Excluded relation | Example of the trap |
|---|---|
| A **part** of the instance | *Person* → organs |
| The **matter or constituent** of the instance | *Statue* → clay |
| A **member** of the instance | *Team*, *Committee* → members |
| A **background condition** | *Plant* → sunlight; anything → spacetime |

If it falls in any row, discard it and return to Step 1 for a different candidate. If no candidate survives → **−D**.

**Step 3 — Test necessity and universality.** Must this hold for *every* instance, in every situation? One instance that could go it alone → **−D**.

**Step 4 — Confirm with the lonely-instance test.** Imagine a world containing one instance of the class and nothing else. Is the description coherent?

- A lone *rock* — fine. → −D
- A lone *student*, with no institution, no teacher, nothing to study — incoherent. → +D

This is the sharpest single test in the set, and it isolates the right notion: it fails precisely when the *definition* of the class reaches outside the instance.

**Do not** treat "can the instance swap partners?" as evidence of −D. A student who transfers schools is still dependent. The quantifier is generic.

<details>
<summary><strong>Inheritance and subsumption rules</strong></summary>

Dependence is **inherited downward**. If a parent is +D, every child is +D — the child's instances are still instances of the parent, so the requirement still bites.

The constraint that fires: **a +D property cannot subsume a −D property.** If your agent labels a class −D whose parent is +D, one of the two labels is wrong, or the hierarchy is. Common real cases:

- *Person* (−D) placed under *Legal Agent* — check whether the parent was correctly labelled.
- *Team* (−D) placed under something like *Social Relationship* (+D).

The reverse is unconstrained: a −D parent may have +D children freely, which is the normal shape for roles. *Student* (+D) under *Person* (−D) is exactly right and should never be flagged.

**Have the agent emit what the class depends on**, as with the unity criterion: `+D (on Educational Institution)` rather than bare `+D`. It forces Step 1 to actually happen, it makes Step 2 auditable, and it surfaces a useful structural signal — if a child's dependee is unrelated to its parent's, you are usually looking at a modelling error.
</details>

<details>
<summary><strong>Dependence vs. anti-rigidity — the confusion to pre-empt</strong></summary>

Roles are typically both `~R` and `+D`, so the two metaproperties correlate heavily in practice and agents start treating them as one signal. They come apart in both directions, and the cases where they do are worth putting in the prompt:

- **+D and rigid:** *Hole*, *Surface*, *Boundary*, *Shadow*, *Dent*. A hole cannot stop being a hole and survive, yet it cannot exist without a host.
- **~R and −D:** *Adolescent*, *Juvenile*, *Sleeping Person*, *Red Thing*. Transient phases requiring no external counterpart.

The rule to state: **rigidity asks whether an instance could lose the property; dependence asks whether an instance needs company.** Answer them separately, and never infer one from the other.
</details>

<details>
<summary><strong>Common confusions to warn the agent against</strong></summary>

| Wrong reading | Correction |
|---|---|
| "It needs its parts to exist, so +D" | Parts are excluded by definition. Every object needs its parts. |
| "It's a collection, so it depends on its members" | Members are excluded too. *Team*, *Committee*, *Orchestra* are −D. |
| "It could exist without *that particular* other thing, so −D" | Dependence is generic. Substitutability is irrelevant. |
| "It needs air / gravity / a planet, so +D" | Background conditions are excluded, or the metaproperty becomes vacuous. Ask whether the other entity appears in the class's *definition*, not merely among the causal preconditions of its existence. |
| "It's a role, so +D" | Usually true, not always. *Adolescent* is a phase with no counterpart. Run the test rather than pattern-matching on role-ness. |
| "It's rigid, so −D" | *Hole* is rigid and +D. See the section above. |
| "It depends on another thing of the same kind, so that doesn't count" | It does count. Only parts, constituents, members, and background conditions are excluded. *Sibling* and *Spouse* are +D on other instances of *Person*. |
| "The thing it depends on no longer exists, so −D" | See the temporal note below. |
</details>

<details>
<summary><strong>The temporal wrinkle: <em>Widow</em>, <em>Orphan</em>, <em>Ex-Employee</em></strong></summary>

A widow requires a spouse who is dead. So does the required entity have to exist *now*, or only at *some* time?

Guarino & Welty's D does not settle this; Welty & Andersen's later **permanence** and **actuality** metaproperties were introduced partly to handle it. For your purposes, the practical move is to decide the convention yourself and state it in the prompt, because agents left to their own devices will split sibling classes inconsistently — labelling *Widow* as −D and *Orphan* as +D within the same run.

The convention I'd suggest: **the dependee must exist at some time, not necessarily concurrently.** Under it, *Widow*, *Orphan*, *Ex-Employee*, *Ruin*, and *Ancestor* are all +D. This keeps the class of past-oriented relational properties together, which is almost always what downstream consumers want.

If you later add permanence/actuality to the pipeline, this is the seam where they attach, and you can then distinguish concurrent dependence (*Student*) from historical dependence (*Widow*) properly rather than by convention.
</details>

<details>
<summary><strong>Near-miss pairs for calibration</strong></summary>

- *Team Member* (+D on *Team*) vs. *Team* (−D). Same relation, opposite verdicts — the asymmetry is the disjointness clause doing its work, and this is the best single example for teaching it.
- *Student* (+D) vs. *Adolescent* (−D). Both transient, both anti-rigid; only one names a counterpart.
- *Hole* (+D, +R) vs. *Rock* (−D, +R). Breaks the role/dependence association.
- *Parent* (+D) vs. *Person* (−D). Parent and child in the hierarchy, and the licit direction of the subsumption constraint.
- *Statue* (−D) vs. *Amount of Clay* (−D). Constitution is excluded in both directions; neither is dependent on the other under D, and the work of separating them is done by unity and rigidity instead.
- *Widow* (+D, historical) vs. *Wife* (+D, concurrent). Where the temporal convention above becomes visible.
- *Passenger* (+D on *Vehicle* or *Journey*) vs. *Pedestrian* (−D). Nearly parallel in surface form, and the dependee filter separates them.
</details>

<details>
<summary><strong>Formal statement, if you want it in documentation</strong></summary>

$\Phi$ is **externally dependent** on $\Psi$ iff:

$$\forall x\, \Box \big( \Phi(x) \rightarrow \exists y\, [\, \Psi(y) \wedge \neg P(y,x) \wedge \neg C(y,x) \wedge \neg P(x,y) \wedge \neg C(x,y) \,] \big)$$

where $P$ is parthood and $C$ is constitution. $\Phi$ is **+D** iff there exists some $\Psi$ satisfying this; **−D** otherwise.

Two things to note if you show this to human reviewers. The existential over $y$ inside the box is what makes the dependence generic rather than specific — the exact point your original wording inverted. And the $\neg P$ / $\neg C$ conjuncts are the disjointness clause; they are the entire content of the metaproperty, since without them the formula is satisfied by nearly every class. Background conditions are not excluded formally, which is why Step 2 needs that row as a pragmatic guard.

As before, I'd keep this out of the agent's prompt. The lonely-instance test outperforms it.
</details>

---

## One note on your example set

*Student* is fine to keep, but "depends on School/Educational Institution" invites the substitutability error described above. If you keep it, add the clause explicitly — "needs *some* institution; which one may change" — because that single hedge blocks the most likely misreading. And I'd replace *Parasite* with *Hole*: it is the standard example, it is unambiguous, and it does double duty by breaking the role⇒dependence association that will otherwise dominate the agent's judgments.

Rigidity is the one left, and it's where the −/~ collapse does the most damage — anti-rigidity is what actually drives OntoClean's subsumption constraints, and a `−R`/`~R` mix-up silently disables most of your violation detection. Send it when ready, and the offer on domain-specific examples stands: if you give me twenty or thirty real class names from your ontology, I'd rather calibrate all four prompts against those than keep polishing the statue-and-clay cases.