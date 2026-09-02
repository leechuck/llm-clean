# Claude Opus 5 (2026-09-01)

## Prompt
I am working a project using AI to determine ontoclean metaproperties in an ontology. documenation about ontoclean can be found here: https://en.wikipedia.org/wiki/OntoClean
The definitions of the  metaproperties technical. I want to make theme easier to understand for an AI agent. I will give you definitions for each metaproperty. Please suggest an alternative definition that is easier to understand.

Please suggest alternative wording for the following description of Identity, and put your response in markdown format:
You are an expert Ontological Analyst specializing in the Identity meta-property from Guarino and Welty (2000).

**Identity (I) - Carries Identity Condition** - Does this property carry an identity condition for its instances?
   - **+I**: The property carries an Identity Condition (IC). Instances can be distinguished and re-identified.
     Examples: Person (has IC like DNA, fingerprints), Physical Object (has spatio-temporal continuity)
   - **-I**: The property does NOT carry an identity condition. No principled way to distinguish instances.
     Examples: Red (what makes one instance of red the same over time?), Amount of Matter

---

## The core problem with the current wording

Before the rewrite, two things in the original will actively mislead an agent:

**1. The Person example teaches the wrong pattern.** "DNA, fingerprints" frames an identity condition as *a distinguishing attribute you could look up* — essentially a database primary key. That's an **identification** criterion (how we recognize which one it is), not an **identity** condition (what makes it the same entity). The distinction matters: identical twins share DNA but are two persons, so DNA isn't sufficient for identity at all. An agent primed on this example will start marking any class with a unique ID field as +I, and any abstract class without one as −I.

**2. "Amount of Matter" is a +I example in the source literature, not −I.** In Guarino & Welty it's the canonical case of *identity without unity*: same matter = same amount of matter (mereological extensionality), so it carries identity, but it isn't a whole, so it's −U/~U. Using it as your −I example will cause systematic misclassification of every mass/substance class in your ontology.

---

## Suggested rewrite

> You are an expert Ontological Analyst specializing in the Identity meta-property from Guarino and Welty (2000).
>
> **Identity (I) — Carries an Identity Condition**
>
> A property carries an identity condition when *being that kind of thing* tells you what counts as one and the same thing. It answers two questions about instances: given two of them, are they the same one or two different ones? And given one of them at two different times, is it still the same one?
>
> **+I — carries an identity condition.** Knowing something is an instance of this class tells you how to count instances and how to track one instance through change. You can meaningfully ask "how many?" and "is this still the same one?"
>
> - *Person* — persons are counted and tracked as persons; a person remains the same person through changes of appearance, belief, location, and cell replacement.
> - *Amount of Matter* — same matter, same amount of matter; it carries identity even though it is not a unified whole.
> - *Organism*, *Statue*, *Building*, *Event* — each brings its own answer to "same one or different one?"
>
> **−I — does not carry an identity condition.** The property can be truly predicated of things, but it supplies no way to count or re-identify them. "How many?" cannot be answered from this property alone.
>
> - *Red* — "how many reds are in this room?" is unanswerable. You must first ask *how many red **what***: cars, patches, pixels. Red describes things; it does not individuate them.
> - *Entity* / *Thing* — applies to everything, distinguishes nothing.
> - *Large*, *Valuable*, *Damaged* — attributions that presuppose some other class to do the counting.

---

## The decision procedure to give the agent

**Primary test — the counting test.** Ask "how many Xs?" with no further context.

- If the question is answerable → **+I**
- If you must first supply another noun ("how many red *cars*") → **−I**

**Secondary test — the persistence test.** Take one instance and change it substantially. Does *being an X* tell you whether it survived as the same X? If yes → +I.

**Confirming test — informativeness.** The criterion must be more than "x is identical to y." Restating identity is not an identity condition. If the only answer you can give is circular, that is evidence of −I.

<details>
<summary><strong>Inherited identity — the most common false negative</strong></summary>

A class carries identity if it *either* supplies its own criterion *or* inherits one from a superclass. It does not need to contribute anything new.

*Student* supplies no identity criterion of its own — nothing about studenthood tells you when two students are one person. But *Student* is subsumed by *Person*, so it inherits Person's criterion and is **+I**. The same holds for *Employee*, *Patient*, *Customer*, *Passenger*.

Agents reliably get this wrong, marking roles as −I because the role itself adds no criterion. The rule to enforce: **if any superclass is +I, the class is +I.** Identity is inherited downward and never lost.

If you want to capture the distinction the agent is groping at, that is a separate metaproperty: **+O** (supplies/owns its identity condition) versus **−O** (merely carries an inherited one). *Person* is +I +O; *Student* is +I −O. Worth adding if your pipeline needs to find where identity criteria actually originate.
</details>

<details>
<summary><strong>Common confusions to warn the agent against</strong></summary>

| Wrong reading | Correction |
|---|---|
| "It has a unique ID / primary key, so +I" | Identifiers are epistemic aids. Ask whether *the kind of thing it is* determines sameness, not whether we happen to have a label for it. |
| "It's abstract, so −I" | Abstract classes can carry identity fine. *Number*, *Musical Work*, *Contract*, *Language* are all +I. |
| "It's a mass noun, so −I" | *Amount of Matter*, *Water*, *Gold* carry identity via their constituent matter. Mass nouns typically fail **unity**, not identity. |
| "Two instances look identical, so −I" | Indistinguishable-in-practice is not the same as no-criterion-in-principle. Two visually identical mugs are still two mugs. |
| "Philosophers disagree about its criterion, so −I" | The requirement is that a criterion exists, not that it is settled or known. Personal identity is famously contested and *Person* is still +I. |
| "I can't state the criterion, so −I" | Try the counting test instead. It usually resolves cases where articulating the criterion is hard. |

**The single sharpest diagnostic:** −I properties are the ones whose instances you cannot count without borrowing a noun from somewhere else.
</details>

<details>
<summary><strong>Near-miss pairs for calibration</strong></summary>

Worth including in the prompt — these are where classifiers break down.

- *Red* (−I) vs. *Colour* (−I) vs. *Red Car* (+I, inherits from Car). Attaching an attribution to a sortal yields a sortal.
- *Amount of Matter* (+I) vs. *Red* (−I). Both feel "stuff-like"; only one answers "how many?"
- *Entity* (−I) vs. *Physical Object* (usually +I via spatio-temporal continuity, though some treatments make it a −I category). If your ontology has a top-level layer, decide this deliberately rather than per-class, and state the decision in the prompt — otherwise the agent will flip-flop across sibling classes.
- *Passenger* (+I, inherited) vs. *Journey* (+I, own criterion). Both are transient; transience is a rigidity question, not an identity one.
</details>

<details>
<summary><strong>Formal statement, if you want it in the prompt</strong></summary>

$\Phi$ carries an identity condition iff there is a relation $\Gamma$ such that for all $x, y$: $\Phi(x) \wedge \Phi(y) \rightarrow (\Gamma(x,y) \leftrightarrow x = y)$, where $\Gamma$ is not itself identity.

I'd suggest **omitting this** from the agent's prompt. Models given the formula tend to reason about the symbols rather than about the class in front of them, and the counting test outperforms it in practice. Keep the formalism in your documentation for human reviewers instead.
</details>

---

## One structural suggestion

Your prompt currently asks the agent a question ("Does this property carry an identity condition?") and then defines the answers. That invites a snap judgment followed by post-hoc justification. Consider inverting it: have the agent run the counting test, then the persistence test, then check superclasses for inherited identity, and only then emit the label. Same information, but the ordering forces the evidence to precede the verdict — which matters most on exactly the role and attribution classes where OntoClean pipelines fail.

Send the next one when ready. If you tell me the domain, I'll swap the textbook examples for classes from your actual ontology, which will help more than any amount of rewording.