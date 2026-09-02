# Claude Opus 5 (2026-09-01)

## Headline problem: your two negative labels are not distinguishable as written

- **−U:** "Instances are not necessarily wholes; parts may be arbitrary."
- **~U:** "Instances are strictly aggregates/sums without integration."

These say close enough to the same thing that an agent has no rule for choosing between them. It will pick based on whether the class name sounds collective ("Group" → ~U) rather than on anything ontological. Three further issues:

**1. −U's actual meaning is missing entirely.** In Guarino & Welty, −U does not mean "not a whole." It means *no single unity criterion covers all instances*. The instances may each be perfectly good wholes — just wholes in different ways. The canonical case is *Legal Agent*, which subsumes both persons (biological/topological unity) and companies (social unity). Every instance is a whole; there is no common criterion. That is −U.

**2. *Amount of Water* is the canonical ~U example, not −U.** Same misfiling as *Amount of Matter* in your Identity prompt — and it is the same class of error. Amounts of matter are **+I, ~U**: they carry identity (same matter, same amount) while carrying anti-unity (an amount of water can be scattered arbitrarily across the universe and remain that same amount). This +I/~U pairing is the one agents find hardest, so getting the example right matters.

**3. *Collection* and *Group* are bad ~U examples.** A specific committee, team, or string quartet is a whole under a social/intentional unity criterion. Treating "aggregate" as automatically ~U teaches exactly the wrong inference. Anti-unity is about **arbitrariness of demarcation**, not about being made of many things.

**4. "Clear mereological structure" invites the wrong reading of +U.** An agent will hear "is it complicated inside?" Unity is not about internal complexity — a featureless marble is +U. It is about whether there is a principled answer to *which parts are its parts*.

---

## Suggested rewrite

> You are an expert Ontological Analyst specializing in the Unity meta-property from Guarino and Welty (2000).
>
> **Unity (U) — Carries a Unity Condition**
>
> A property carries unity when *being that kind of thing* tells you where the thing stops. For any instance and any part of the world, it answers: is this part of that instance, or not? The answer must come from the kind itself, not from an arbitrary decision.
>
> Unity is about boundaries at a moment in time. It is not about how complex the thing is, how many parts it has, or whether the parts are touching.
>
> **+U — carries unity.** All instances are wholes, and one and the same criterion makes them wholes. Name the criterion.
>
> - *Person* — biological and topological: the parts are the ones participating in this organism's life.
> - *Car* — functional: the parts are the ones assembled to serve this vehicle's operation.
> - *Lake* — topological/morphological: the water bounded by this basin.
> - *String Quartet* — social/intentional: the members recognised as belonging to this ensemble. Aggregates can be +U.
>
> **−U — does not carry unity.** The property fails to supply a *common* criterion. Its instances may each be genuine wholes, but by different criteria. This is the label for classes that cut across kinds.
>
> - *Legal Agent* — persons are wholes one way, corporations another; nothing unifies both.
> - *Red Thing* — a red car is a whole, a red apple is a whole, a red patch of sky is a whole, and there is no shared answer to "which parts?"
> - *Physical Object* — if your ontology admits both organisms and arbitrary lumps, this is −U.
>
> **~U — carries anti-unity.** Every instance can be arbitrarily demarcated. There is no principled boundary at all — you could always have drawn the line elsewhere and had an equally good instance of the kind.
>
> - *Amount of Water* — any quantity of water counts; scattered across three continents it is still that amount. Note this is **+I and ~U** together.
> - *Amount of Matter*, *Gold*, *Sand*
> - *Arbitrary Spatial Region*, *Undetached Rabbit Part*

---

## The decision procedure to give the agent

Run in order:

**Step 1 — Attempt to name the criterion.** Ask: "For an instance of this class, what makes something a part of *it* rather than of something else, or of nothing?" Pick from:

| Criterion | Test | Typical classes |
|---|---|---|
| **Topological** | Connectedness — parts are physically joined | *Rock*, *Puddle*, *Island* |
| **Morphological** | Shape or form bounds it | *Statue*, *Constellation*, *Knot* |
| **Functional** | Parts contribute to a common purpose | *Car*, *Bicycle*, *Hammer* |
| **Social / intentional** | Recognition, membership, or convention bounds it | *Committee*, *Nation*, *Orchestra* |
| **Biological** | Parts participate in one life process | *Organism*, *Tree* |

If exactly one criterion applies to **all** instances → **+U**.

**Step 2 — If a criterion exists but different instances need different ones → −U.** Diagnostic: can you name two instances of this class that are wholes for unrelated reasons? If yes, −U.

**Step 3 — If no criterion applies to any instance → ~U.** Confirming test, the *arbitrary redrawing test*: take an instance, add or remove a bit at random. Is the result still a perfectly good instance of the same kind, with no sense that you have damaged or incompleted anything? If yes → ~U.

That third test is the sharpest single discriminator in the set. *Car*: remove a wheel at random and you have a damaged car — fails, so not ~U. *Amount of Water*: remove a millilitre and you have a perfectly good amount of water — passes, so ~U.

<details>
<summary><strong>Inheritance and subsumption rules</strong></summary>

Unity does not behave like identity, so the rules from your Identity prompt do not transfer.

- **+U is inherited downward.** If a superclass carries unity criterion $\omega$, every instance of every subclass satisfies $\omega$. So under a +U parent, all children are +U. An agent labelling a child of *Person* as −U has made an error.
- **~U cannot subsume +U.** This is the OntoClean constraint that actually fires. *Statue* (+U, morphological) must not be placed under *Amount of Clay* (~U). If your ontology has this shape, that is a finding to report, not a labelling problem to resolve.
- **−U is the permissive middle.** It can sit above +U children freely — that is what makes it useful for cross-cutting abstractions like *Legal Agent*.
- **Different +U criteria conflict.** Two classes carrying *incompatible* unity criteria cannot subsume one another even though both are +U. Worth having the agent record *which* criterion it identified in Step 1, not just the label — otherwise you cannot check this constraint downstream.
</details>

<details>
<summary><strong>Common confusions to warn the agent against</strong></summary>

| Wrong reading | Correction |
|---|---|
| "It's a collection/group/set, so ~U" | Ask whether membership is principled. *Committee* is +U (social). *Arbitrary Pile* is ~U. The word "group" decides nothing. |
| "Its parts are scattered, so ~U" | Spatial disconnection is compatible with unity. A *Nation*'s territory may be non-contiguous; a *Constellation* is unified morphologically. Only topological unity requires contact. |
| "It's simple with no parts, so −U or ~U" | Simplicity is maximal unity, not absent unity. *Elementary Particle* is +U. |
| "It's a mass noun, so ~U" | Usually right, but check for a bounding criterion. *Water* is ~U; *Glass of Water*, *Puddle*, *Raindrop* are +U. The bounding container or form does the work. |
| "It's abstract, so no unity" | *Musical Work*, *Contract*, *Theorem* carry unity. |
| "It's +I, so it must be +U" | The single most damaging inference. *Amount of Matter* is +I and ~U. Identity answers "how many / still the same one?"; unity answers "which parts?" They are independent. |
| "Instances change parts over time, so −U" | Unity is evaluated at a time. Persons replace cells and remain +U. Part-change over time is an identity question. |
</details>

<details>
<summary><strong>Near-miss pairs for calibration</strong></summary>

- *Amount of Water* (~U) vs. *Puddle* (+U, topological) vs. *Bottle of Water* (+U, containment). Identical stuff, three different verdicts — the boundary comes from outside the substance.
- *Committee* (+U, social) vs. *Three People I Just Pointed At* (~U). Both are collections of persons.
- *Legal Agent* (−U) vs. *Person* (+U). Parent and child, different labels — shows −U is not "less unified" but "not uniformly unified."
- *Car* (+U, functional) vs. *Pile of Car Parts* (~U). Same matter, and the functional criterion is what disappears.
- *Constellation* (+U, morphological) vs. *Arbitrary Set of Stars* (~U). Rules out "scattered ⇒ ~U."
- *Person* (+U) vs. *Amount of Matter Constituting a Person* (~U). The classic constitution pair; the two coincide materially and differ in unity, which is precisely why they must be distinct classes.
</details>

<details>
<summary><strong>Formal statement, if you want it in documentation</strong></summary>

$\Phi$ **carries unity** iff there is a single equivalence-like relation $\omega$ such that for all $x$: $\Phi(x) \rightarrow x$ is a whole under $\omega$.

$\Phi$ **carries anti-unity** iff every instance of $\Phi$ can possibly be a non-whole:
$$\forall x\, \big(\Phi(x) \rightarrow \Diamond\, \neg \exists \omega\, [\,x \text{ is a whole under } \omega\,]\big)$$

$\Phi$ is **−U** iff it does not carry unity — the weak negation, which is entailed by ~U but not equivalent to it. As with Identity, I'd keep this out of the agent's prompt; the arbitrary-redrawing test is more reliable in practice than the modal formulation, which tends to get read as "is it *possible* to imagine vagueness here?" — a question to which the answer is always yes.
</details>

---

## One structural suggestion

Have the agent **emit the unity criterion it identified**, not just the label — e.g. `+U (functional)` rather than `+U`. Three benefits: it forces Step 1 to actually happen rather than being skipped in favour of a vibe judgment; it makes the −U determination checkable, since −U should come with two named conflicting criteria; and it gives you the data needed to detect incompatible-criterion subsumption violations later. A bare `+U` on both parent and child hides a real error when the criteria differ.

Next one whenever you're ready. Rigidity is where I'd expect the −/~ collapse to bite hardest, so if you send that definition I'll pay particular attention to it — and the offer on domain-specific examples still stands.
