# Claude Opus 5 (2026-09-01)

## Headline problem: *Student* appears under both `−R` and `~R`

Your `−R` examples list *Student* ("a person can become/stop being a student"). Your `~R` examples list "Role (like **Student**, Employee)." The agent is shown the same class as an instance of two different labels, in one prompt, forty words apart.

This is not a cosmetic slip — it is the metaproperty's central difficulty appearing as a contradiction in the instructions. The reason it happened is that the labels overlap logically: **`~R` entails `−R`**. Anything anti-rigid *is* non-rigid. So the three values are not a partition, and any prompt that presents them as one will produce whatever the model happens to feel like on a given class.

The fix is a **labelling convention, stated explicitly**: always report the strongest true value, and reserve `−R` for the genuinely mixed case. Which brings us to the second problem.

**`−R`'s real content is missing.** "Not essential to some instances" is under-specified in a way that lets *Student* in. The interesting and correct reading of `−R` is: **some instances have the property essentially, others contingently.** The standard name for this in the OntoClean literature is **semi-rigid**, and simply using that word does most of the explanatory work your current wording is failing to do. *Student* is not semi-rigid — no student holds studenthood essentially — so it is `~R`, unambiguously.

Two more:

**"Essential NOT to be essential (contingent by definition)" is opaque.** It is a compressed reading of $\forall x\,\Box(\varphi(x) \rightarrow \Diamond\neg\varphi(x))$, but as English it will not survive contact with a hard case. The plain version: *every* instance must be able to exist without the property.

**"Anything that is a person is necessarily a person" teaches nothing.** That sentence is true of literally every class under a *de dicto* reading — anything that is a student is necessarily a student, in the same empty sense. Rigidity is a *de re* claim about individuals, and this example models exactly the reasoning that cannot distinguish the cases. Replace it with the survival test.

---

## Suggested rewrite

> You are an expert Ontological Analyst specializing in the Rigidity meta-property from Guarino and Welty (2000).
>
> **Rigidity (R) — Is the property essential to its instances?**
>
> A property is essential to an individual when that individual **could not exist without it**. Not "would be different without it" — could not exist at all.
>
> The question is always about a particular individual: take one instance, imagine it losing the property, and ask whether *the thing itself* survives the loss. A person who stops being a student is still there. A person who stops being a person is not.
>
> Report the **strongest** value that holds. `~R` is stronger than `−R`; if a property is anti-rigid, label it `~R` and not `−R`.
>
> **+R — rigid.** No instance can lose the property and continue to exist. Losing it *is* ceasing to be.
>
> - *Person* — nothing survives its own ceasing-to-be-a-person.
> - *Statue* — squash it and the statue is gone, even though the clay remains.
> - *Amount of Matter*, *Organism*, *Event*, *Number*, *Hole*
>
> **~R — anti-rigid.** *Every* instance is able to exist without the property. No instance holds it essentially.
>
> - *Student* — every student could exist without being one, and typically has.
> - *Employee*, *Passenger*, *Tenant* — roles.
> - *Child*, *Adult*, *Caterpillar*, *Butterfly* — phases.
> - *Widow*, *Graduate* — still `~R`. See the note on irreversible phases; the test is modal, not about the future.
>
> **−R — semi-rigid.** The mixed case: **some** instances hold the property essentially, **others** contingently. The class contains both kinds. Use this label only when you can name an instance of each kind.
>
> - *Weapon* — a sword is essentially a weapon; a rock picked up in a fight is not.
> - *Hard* — a diamond is essentially hard; a lump of cooled wax is contingently hard.
> - Abstractions that union a rigid class with an anti-rigid one, e.g. *Agent* over both *Person* (+R) and *Authorised Signatory* (~R).
>
> If you are reaching for `−R` and cannot name an instance that holds the property **essentially**, the answer is `~R`.

---

## The decision procedure to give the agent

**Step 1 — The survival test.** Take an instance. Imagine it ceasing to be an X. Does the individual still exist?

- **No** — ceasing to be an X means going out of existence → candidate `+R`.
- **Yes** — something survives → candidate `~R`.

**Step 2 — The survivor-naming test.** This is the sharpest discriminator, and it resolves most disagreements in Step 1. When the property is lost, ask: **is there a natural noun for what remains?**

| Class | Lose the property, and you have… | Verdict |
|---|---|---|
| *Student* | a person | `~R` |
| *Passenger* | a person | `~R` |
| *Caterpillar* | the same insect | `~R` |
| *Statue* | some clay — but no statue | `+R` |
| *Person* | a corpse or nothing — not that person | `+R` |

If the survivor has a name and it is the *same individual*, the property is not rigid. If the only thing left is different matter or a different entity, it is rigid.

**Step 3 — Quantify over the whole class.**

- Holds for **every** instance (no survivor ever) → `+R`
- Fails for **every** instance (survivor always) → `~R`
- **Mixed** → `−R (semi-rigid)`, and name one instance of each kind in your justification.

**Step 4 — Guard against false `−R`.** Before emitting `−R`, state which instance holds the property *essentially*. If you cannot, revise to `~R`. This single requirement eliminates the most damaging error in the set.

<details>
<summary><strong>The irreversible-phase trap — the error I would most expect from a competent model</strong></summary>

Anti-rigidity requires that every instance *possibly* lacks the property: $\Diamond\neg\varphi(x)$. It does **not** require that instances can *stop* having it.

An agent reasoning forward in time will get these wrong:

- *Adult* — you cannot stop being an adult, so it looks rigid. But every adult **was** a child, which demonstrates that this very individual can exist without being an adult. → `~R`
- *Widow*, *Ex-Employee*, *Graduate*, *Convicted Felon*, *Deceased Person*, *Ruin* — same shape. Irreversible, and all `~R`.

The rule to state in the prompt: **"could this individual exist without the property?" — at any time, past or future, or in any counterfactual situation.** Never "could it lose the property going forward."

This trap interacts badly with your Dependence prompt, where *Widow* was the temporal edge case. An agent that marks *Widow* as `+R` here will then be permitted by the O gate to treat it as an identity supplier, and you will get a `+O` label on a phase — which is precisely the failure mode the rigidity clause of Definition 6 exists to prevent.
</details>

<details>
<summary><strong>Inheritance and subsumption rules</strong></summary>

Rigidity behaves unlike the others: **`+R` is not inherited downward.** A rigid class can have anti-rigid children — *Student* under *Person* is correct and must never be flagged.

**`~R` propagates strictly downward.** If $\varphi \sqsubseteq \psi$ and $\psi$ is anti-rigid, then $\neg\psi(x) \rightarrow \neg\varphi(x)$, so every instance of $\varphi$ can also exist without $\varphi$. Every subclass of an anti-rigid class is anti-rigid. A `+R` class under a `~R` parent is a **contradiction**, not a finding requiring judgment.

**The constraint that fires: `~R` cannot subsume `+R`.** This is the workhorse of OntoClean — the check that catches *Person* modelled under *Student*, *Organisation* under *Customer*, *Vehicle* under *Rental Unit*. It is the single most productive violation detector in the framework.

And it is why the `−R`/`~R` collapse is expensive: the constraint is stated on `~R`, so a role wrongly labelled `−R` is **silently exempted**. No error is raised; the check simply never runs. A pipeline that over-uses `−R` will report a clean ontology while detecting nothing.

**Have the agent emit its Step 4 justification**, as with the unity criterion and the dependee. For `−R`, that means naming the essential-holder instance. It is cheap, it makes the label auditable, and `−R` verdicts with an empty justification field are your highest-yield review queue.
</details>

<details>
<summary><strong>Common confusions to warn the agent against</strong></summary>

| Wrong reading | Correction |
|---|---|
| "Anything that is an X is necessarily an X, so +R" | Trivially true of every class. Rigidity is a claim about individuals surviving loss, not a tautology about class membership. Run the survivor-naming test. |
| "Instances can change over time, so −R or ~R" | Rigidity is about losing *this property*, not about changing in other respects. Persons change constantly and are `+R`. |
| "It's irreversible, so +R" | See the trap above. *Adult*, *Widow*, *Graduate* are all `~R`. |
| "Not every instance could lose it, so −R" | Check whether you mean *could lose going forward* — an adult cannot, but is still `~R`. `−R` requires an instance holding the property **essentially**. |
| "It's a role, so ~R" | Almost always right, but confirm rather than pattern-match; the same shortcut applied to *Hole* (a rigid dependent) gives the wrong answer. |
| "It's `+D`, so `~R`" | `Hole`, `Surface`, `Shadow` are `+D` and `+R`. Dependence and rigidity are independent — the same warning as in the Dependence prompt, from the other side. |
| "The class might not exist in some possible world, so not `+R`" | Rigidity says nothing about whether the property is *instantiated* in a world. It quantifies over instances: each one, necessarily, keeps it. |
| "All Xs have property P, so X is `+R`" | Universal attribution is not essence. "All swans are birds" is about swans, not about rigidity of *Swan*. |
| "Its parent is `+R`, so it's `+R`" | Rigidity is not inherited downward. Only `~R` propagates, and only downward. |
</details>

<details>
<summary><strong>Near-miss pairs for calibration</strong></summary>

- *Student* (`~R`) vs. *Weapon* (`−R`). The pair to include verbatim, since it is the distinction your current prompt collapses. Both "can be gained and lost"; only *Weapon* has essential holders.
- *Adult* (`~R`) vs. *Person* (`+R`). Both irreversible from the inside. Isolates the modal-not-temporal reading.
- *Statue* (`+R`) vs. *Amount of Clay* (`+R`) vs. *Sculpted Object* (`~R`, if it means "currently shaped as"). Same material situation, and the verdict turns on whether the class names a kind or a state.
- *Caterpillar* (`~R`) vs. *Insect* (`+R`). Parent and child, opposite labels, licit direction.
- *Hole* (`+R`, `+D`) vs. *Tenant* (`~R`, `+D`). Breaks the dependence⇒anti-rigidity association.
- *Deceased Person* (`~R`) vs. *Corpse* (`+R`, on most treatments). Nearly co-extensive, different labels — worth a deliberate house decision rather than per-class improvisation.
- *Red Thing* — I would **remove** this from your examples. It is `~R` on the natural reading, but if some things are essentially red it is `−R`, and it is genuinely contested. Contested examples in a prompt license the model to treat all its judgments as soft.
</details>

<details>
<summary><strong>Formal statement, if you want it in documentation</strong></summary>

$$\text{Rigid: } \quad \forall x\, \Box\big(\varphi(x) \rightarrow \Box\varphi(x)\big)$$

$$\text{Anti-rigid: } \quad \forall x\, \Box\big(\varphi(x) \rightarrow \Diamond\neg\varphi(x)\big)$$

Non-rigid is the plain negation of rigid, so $\text{anti-rigid} \models \text{non-rigid}$. Semi-rigid is the useful residue:

$$\text{Semi-rigid: } \quad \exists x\,\big(\varphi(x) \wedge \Box\varphi(x)\big) \;\wedge\; \exists y\,\big(\varphi(y) \wedge \Diamond\neg\varphi(y)\big)$$

Note that the entailment is what makes the three values a non-partition, and therefore what made your prompt's double-listing of *Student* possible. If you want mutually exclusive labels — and for a classifier you do — `−R` must be **defined** as semi-rigid, not as "not rigid." Say so in the prompt rather than leaving it to the examples, which is where the current version fails.

As before, keep this out of the agent's prompt. The modal operators invite the reading "is it *conceivable* that…", to which the answer is always yes, and the survivor-naming test outperforms it substantially.
</details>

---

## Two notes on the set as a whole

**On the labelling convention.** The `−R`/`~R` overlap has an exact analogue in Unity, which your Unity prompt handled by giving `−U` its own positive content ("no *common* criterion"). Do the same here — `−R` means semi-rigid — and state the report-the-strongest rule in all three trichotomous prompts. Consistency across prompts matters more than the wording of any one of them, because the agent generalises from whichever prompt it saw last.

**On the pipeline.** With R settled, the ordering is: **I → R → O**, with U and D independent. The O gates read the R label rather than re-deriving it, so any `−R`/`~R` error here propagates into O and disables the disjointness checks downstream. If you run only one validation pass, make it the cross-prompt consistency check: no class labelled `+O` with a non-`+R` R-label, no `+R` class under a `~R` parent, no `−R` verdict lacking a named essential-holder.

That's the four core metaproperties plus O. If you want to go further, **permanence** and **actuality** (Welty & Andersen 2005) are the natural next additions and would let you replace the temporal convention I suggested for *Widow* with a principled treatment. And the offer stands on domain examples — twenty or thirty real class names from your ontology would let me calibrate all five prompts against cases you actually have, which at this point would be worth more than further work on the wording.