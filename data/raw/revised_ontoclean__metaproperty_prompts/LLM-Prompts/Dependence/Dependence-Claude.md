**Dependence (D) — External Dependence**

A property is externally dependent when nothing can be an instance of it *all by itself*. Being that kind of thing requires some **other, separate** entity to exist alongside it.

"Separate" is what makes this metaproperty non-trivial. The required entity must be **outside** the instance — not one of its parts, not the matter it is made of, not one of its members. Everything depends on its own parts; that is not what is being measured here. Nor does it count that instances need favourable background conditions such as air, gravity, or spacetime.

The requirement is **generic**: some instance of the other class must exist. It need not be one particular individual, and the instance may be free to swap which one it stands in relation to.

This metaproperty has only two values. There is no anti-dependence.

**+D — externally dependent.** Every instance, necessarily, coexists with some separate entity of another kind. Usually you can see the dependence in the definition of the class: you cannot say what the class *is* without mentioning the other thing.

- *Student* — needs some educational institution or teacher. Which one may change; that one exists cannot.
- *Parent* — needs a child. The child is not part of the parent.
- *Employee*, *Passenger*, *Tenant*, *Patient* — roles, each naming its counterpart.
- *Hole* — needs a host object to be a hole in. Note this one is **+D and rigid**; dependence is not confined to roles.
- *Surface*, *Boundary*, *Shadow* — dependent on what they bound or are cast by.

**−D — not externally dependent.** An instance could exist in a world containing nothing else of relevance. It may well have parts, constituents, and members it could not survive without — that does not make it dependent.

- *Person* — a person needs organs, but organs are parts.
- *Apple*, *Rock*, *Physical Object*
- *Team* — a team needs members, but members are members. Dependence excludes them, so *Team* is −D even though *Team Member* is +D.

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