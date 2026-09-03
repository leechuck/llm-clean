# Own Identity (O)

A property **supplies** an identity condition when it is the **origin** of the answer to "same one or different one?" Carrying identity (`+I`) means the class has an answer; supplying it means the answer starts here rather than being inherited from further up.

Three requirements, all of which must hold:

1. **Rigid (`+R`).** Only rigid classes can supply identity. The criterion must be **global** — valid whenever the instance exists, not merely while it happens to fall under this class. A criterion that stops tracking the individual once a role or phase ends is *local* and does not count.
2. **Carries an IC (`+I`).** A class cannot supply what it does not have. Hence `+O → +I ∧ +R`.
3. **Adds something.** The criterion must not be carried by *all* subsuming classes. A rigid subclass that introduces a new, compatible criterion on top of an inherited one is still `+O`; supply stacks.

`+O` is **taxonomy-relative**: the same class flips label depending on what sits above it, so evaluate it against the class's ancestors and their ICs, after `I` and `R` are settled.

**`+O`** — *Person* (personal-identity criteria no broader class provides), *Amount of Matter* (same constituent matter), *Statue* (sameness of form), *Organism*, *Event*, *Number*, *Set*.

**`−O`** — three distinct reasons, worth recording separately: **not rigid** (*Student*, *Employee*, *Passenger*, *Adult* — student numbers and employee IDs are local criteria, identity comes from *Person*); **rigid but adds nothing** (*Mammal* under *Organism*, *Integer* under *Number*); **carries no IC at all** (*Red*, *Entity*, *Large*).

**Test:** apply the candidate criterion at a time when the individual is *not* an instance of the class. If it still tracks them, it is global → `+O` is possible. If it lapses, it is local → `−O`.

Where a subclass appears to require a criterion *incompatible* with its parent's, do not label it `+O` — report a subsumption violation. ICs may be augmented but never overridden, and two classes supplying incompatible criteria (*Statue* vs. *Amount of Clay*) must be disjoint.