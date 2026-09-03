# Revised Metaproperty Prompts

## LLM revisions
Claude, Gemini, and ChatGPT were instructed to revise/simplify the hardcoded prompts for determining dependence, identity, own identity, rigidity, and unity found in `llm-clean/src/llm_clean/ontology/prompts.py`. The LLMs were access through OpenRouter, and the LLMs selected (on `2026-09-01`) were:
* Gemini Pro Latest 
* GPT-5.5 Pro
* Claude Opus 5

Each LLM was given the following prompt:  
> I am working a project using AI to determine ontoclean metaproperties in an ontology. documenation about ontoclean can be found here: https://en.wikipedia.org/wiki/OntoClean
The definitions of the  metaproperties technical. I want to make theme easier to understand for an AI agent. I will give you definitions for each metaproperty. Please suggest an alternative definition that is easier to understand.

After the LLM responded, each metaproperty was revised using the prompt:  
> Please suggest alternative wording for the following description of `<metaproperty>`, and put your response in markdown format:  
`<insert corresponding prompt from prompts.py>`

See **Metaproperty prompts supplied to LLMs** section below for the prompts used.

Results of the prompts are saved in the directories/files:

* Dependence
  * [Dependence-ChatGPT.md](Dependence/Dependence-ChatGPT.md)
  * [Dependence-Claude.md](Dependence/Dependence-Claude.md)
  * [Dependence-Gemini.md](Dependence/Dependence-Gemini.md)

* Identity
  * [Identity-ChatGPT.md](Identity/Identity-ChatGPT.md)
  * [Identity-Claude.md](Identity/Identity-Claude.md)
  * [Identity-Gemini.md](Identity/Identity-Gemini.md)

* Own-Identity
  * [Own-Identity-ChatGPT.md](OwnIdentity/OwnIdentity-ChatGPT.md)
  * [Own-Identity-Claude.md](OwnIdentity/OwnIdentity-Claude.md)
  * [Own-Identity-Gemini.md](OwnIdentity/OwnIdentity-Gemini.md)

* Rigidity
  * [Rigidity-ChatGPT.md](Rigidity/Rigidity-ChatGPT.md)
  * [Rigidity-Claude.md](Rigidity/Rigidity-Claude.md)
  * [Rigidity-Gemini.md](Rigidity/Rigidity-Gemini.md)

* Unity
  * [Unity-ChatGPT.md](Unity/Unity-ChatGPT.md)
  * [Unity-Claude.md](Unity/Unity-Claude.md)
  * [Unity-Gemini.md](Unity/Unity-Gemini.md)

## Synthesized revision 
For each LLM specific metaproperty, the LLM was asked to synthesize all three metaproperty file into a single concise instruction for determining the metaproperty. The prompt used was:

> The attached files contain three proposed revisions of instructions for an LLM to evaluate Ontoclean's `<metaproperty name>` metaproperty. Please review the metaproperty revisions and create a single concise instruction. Do not include tests, formal definitions, or other filters. Only return the revised instruction. Format your answer in markdown.

Due to excessive wordiness by Claude, I had to add instructions to only return the the revision:  
> The attached files contain three proposed revisions for instructions on LLM how to evaluate Ontoclean's `<metaproperty name>` metaproperty. Please review the metaproperty revisions and create a single concise instruction. **I don't need the labels, decision procedure, errors to avoid. I only need the revision. Only return the suggested revision, and nothing else.** Format your answer in markdown.

The synthesized revisions are in the Synthesized directories:
* Synthesized/Dependence
  * [Dependence-synthesized-ChatGPT.md](Synthesized/Dependence/Dependence-synthesized-ChatGPT.md)
  * [Dependence-synthesized-Claude.md](Synthesized/Dependence/Dependence-synthesized-Claude.md)
  * [Dependence-synthesized-Gemini.md](Synthesized/Dependence/Dependence-synthesized-Gemini.md)
* Synthesized/Identity
  * [Identity-synthesized-ChatGPT.md](Synthesized/Identity/Identity-synthesized-ChatGPT.md)
  * [Identity-synthesized-Claude.md](Synthesized/Identity/Identity-synthesized-Claude.md)
  * [Identity-synthesized-Gemini.md](Synthesized/Identity/Identity-synthesized-Gemini.md)
* Synthesized/Own-Identity
  * [Own-Identity-synthesized-ChatGPT.md](Synthesized/Own-Identity-synthesized-ChatGPT.md)
  * [Own-Identity-synthesized-Claude.md](Synthesized/Own-Identity-synthesized-Claude.md)
  * [Own-Identity-synthesized-Gemini.md](Synthesized/Own-Identity-synthesized-Gemini.md)
* Synthesized/Rigidity
  * [Rigidity-synthesized-ChatGPT.md](Synthesized/Rigidity/Rigidity-synthesized-ChatGPT.md)
  * [Rigidity-synthesized-Claude.md](Synthesized/Rigidity/Rigidity-synthesized-Claude.md)
  * [Rigidity-synthesized-Gemini.md](Synthesized/Rigidity/Rigidity-synthesized-Gemini.md)
* Synthesized/Unity
  * [Unity-synthesized-ChatGPT.md](Synthesized/Unity/Unity-synthesized-ChatGPT.md)
  * [Unity-synthesized-Claude.md](Synthesized/Unity/Unity-synthesized-Claude.md)
  * [Unity-synthesized-Gemini.md](Synthesized/Unity/Unity-synthesized-Gemini.md)

## Tests for metaproperties
Interestingly, Gemini also supplied "tests" for determining metaproperties.

### Dependence
To help the AI agent determine if a concept is Dependent, provide it with these practical thought experiments:

**The "Floating in a Void" Test:**
*   Imagine this object existing entirely by itself in an otherwise empty universe. Does the concept still make logical sense?
    *   *If NO* $\rightarrow$ likely **+D** (You cannot have a "Student" in a void with no schools, or a "Border" with no countries. They depend on outside things).
    *   *If YES* $\rightarrow$ likely **-D** (A "Rock" or a "Dog" can logically exist floating alone in an empty universe. They are independent).

**The "Definition Requirement" Test:**
*   If you write down the definition of this concept, are you forced to include another distinct, external entity? *(Note: Do not count the object's own internal parts).*
    *   *If YES* $\rightarrow$ likely **+D** (Defining a "Parasite" forces you to mention a "Host").
    *   *If NO* $\rightarrow$ likely **-D** (Defining a "Tree" only requires talking about the tree and its own parts).

### Identity
To help the AI agent accurately classify this property, you can include these simple true/false questions in its prompt:

**The "Same One" Test (Re-identification):**
*   If I see an instance of this today, and an instance tomorrow, is there a factual way to prove they are the *exact same* individual, rather than just two identical-looking copies?
    *   *If YES* $\rightarrow$ likely **+I** (I can prove this is the exact same dog using its microchip).
    *   *If NO* $\rightarrow$ likely **-I** (I cannot prove this is the exact same "redness" or "amount of water" without referring to the cup or the car it belongs to).

**The "Distinction" Test:**
*   If there are two of these right next to each other, is there a built-in rule to explain why there are two instead of one?
    *   *If YES* $\rightarrow$ likely **+I** (Two people have two distinct bodies/minds).
    *   *If NO* $\rightarrow$ likely **-I** (Two instances of "red" next to each other just blend into a larger area of red).

### Own Identity.
To help the AI agent determine if a concept supplies its *Own* Identity, provide it with these practical tests:

**The "Parent Category" Test:**
*   Does this concept rely on a deeper, more basic noun to explain how we tell instances apart?
    *   *If YES* $\rightarrow$ **-O** (A "Teacher" relies on "Person" for its identity rules. "Teacher" just borrows it).
    *   *If NO* $\rightarrow$ likely **+O** ("Person" doesn't rely on a deeper concept to explain human identity).

**The "Role vs. Essence" Test:**
*   Is this concept just a temporary role or a job that the object is currently doing?
    *   *If YES* $\rightarrow$ **-O** (Roles like "President," "Customer," or "Pet" never supply their own identity; they borrow it from the underlying human or animal).
    *   *If NO* $\rightarrow$ potentially **+O** (Essences like "Human," "Dog," or "Car" supply the fundamental identity).

### Rigidity
To help the AI agent determine the Rigidity of a concept, provide it with these practical thought experiments:

**The "Cease to Exist" Test:**
*   If an instance of this concept suddenly stops being [Concept], is it completely destroyed or dead?
    *   *If YES for all instances* $\rightarrow$ **+R** (If a Tree stops being a Tree, it's just dead wood—it doesn't exist as a tree anymore).
    *   *If NO for all instances* $\rightarrow$ **~R** (If a Mayor stops being a Mayor, they are not destroyed, they are just a regular citizen again).

**The "Role vs. Species" Test:**
*   Is this concept a temporary job, a societal role, or a phase of life that something *goes through*?
    *   *If YES* $\rightarrow$ likely **~R** (Puppy, Customer, Patient).
    *   *If NO, it's what the thing fundamentally IS* $\rightarrow$ likely **+R** (Animal, Human, Mountain).

**The "Paint/Change" Test (for -R):**
*   Is this concept a physical trait (like a color, shape, or size) where some things have it by nature (can't lose it) but other things just have it by accident (can lose it)?
    *   *If YES* $\rightarrow$ **-R** ("Red" is -R because a ruby must be red, but a painted wall can change color).

### Unity
To help the AI agent accurately classify a concept, you can include these simple true/false "tests" in its prompt:

**The Division Test:**
*   If I cut this in half, are both halves still called by the same name?
    *   *If NO* $\rightarrow$ likely **+U** (A car cut in half is not a car).
    *   *If YES* $\rightarrow$ likely **-U** (Water cut in half is still water).

**The Merging Test:**
*   If I push two of these together, do they just become one larger version of the same thing?
    *   *If NO* $\rightarrow$ likely **+U** (Two apples pushed together are still two apples, not one big apple).
    *   *If YES* $\rightarrow$ likely **-U** (Two piles of sand pushed together become one pile of sand).

**The Group Test:**
*   Is this concept just a word for "a bunch of other things"?
    *   *If YES* $\rightarrow$ likely **~U** (A "forest" is just a bunch of trees; a "crowd" is a bunch of people).


## Metaproperty prompts supplied to LLMs

### Dependence
Please suggest alternative wording for the following description of Dependence, and put your response in markdown format:
You are an expert Ontological Analyst specializing in the Dependence meta-property from Guarino and Welty (2000).

**Dependence (D)** - Do instances intrinsically depend on other entities?
   - **+D (Dependent)**: Instances necessarily depend on other entities to exist.
     Examples: Student (depends on School/Educational Institution), Parasite (depends on Host)
   - **-D (Independent)**: Instances can exist without depending on specific other entities.
     Examples: Person (independent), Physical Object (independent)
     
### Identity
Please suggest alternative wording for the following description of Dependence, and put your response in markdown format:
You are an expert Ontological Analyst specializing in the Identity meta-property from Guarino and Welty (2000).

**Identity (I) - Carries Identity Condition** - Does this property carry an identity condition for its instances?
   - **+I**: The property carries an Identity Condition (IC). Instances can be distinguished and re-identified.
     Examples: Person (has IC like DNA, fingerprints), Physical Object (has spatio-temporal continuity)
   - **-I**: The property does NOT carry an identity condition. No principled way to distinguish instances.
     Examples: Red (what makes one instance of red the same over time?), Amount of Matter

### Own Identity
Please suggest alternative wording for the following description of Dependence, and put your response in markdown format:
You are an expert Ontological Analyst specializing in the Own Identity meta-property from Guarino and Welty (2000).

**Own Identity (O) - Supplies Identity Condition** - Does this property supply its OWN identity condition?
   - **+O**: Supplies its own global identity condition.
     Examples: Person (supplies own IC), Physical Object (supplies own IC)
   - **-O**: Does not supply own IC (inherits it from a more general property, or has none).
     Examples: Student (inherits IC from Person), Red (has no IC to supply)

**IMPORTANT CONSTRAINT**: If +O, then +I must be true. You cannot supply an IC without carrying one.


### Rigidity
Please suggest alternative wording for the following description of Dependence, and put your response in markdown format:
You are an expert Ontological Analyst specializing in the Rigidity meta-property from Guarino and Welty (2000).

**Rigidity (R)** - Analyze whether the property is essential to all its instances:
   - **+R (Rigid)**: Essential to ALL instances in ALL possible worlds.
     Examples: Person (anything that is a person is necessarily a person), Physical Object
   - **-R (Non-Rigid)**: Not essential to some instances; instances can gain/lose it.
     Examples: Student (a person can become/stop being a student), Red Thing
   - **~R (Anti-Rigid)**: Essential NOT to be essential (contingent by definition).
     Examples: Role (like Student, Employee), Phase (like Child, Adult)

### Unity
You are an expert Ontological Analyst specializing in the Unity meta-property from Guarino and Welty (2000).

**Unity (U)** - Are instances of this property wholes with integrated parts?
   - **+U (Unifying)**: Instances are intrinsic wholes with clear mereological structure.
     Examples: Person (integrated biological system), Car (functional whole)
   - **-U (Non-Unifying)**: Instances are not necessarily wholes; parts may be arbitrary.
     Examples: Red Thing (scattered red objects), Amount of Water
   - **~U (Anti-Unity)**: Instances are strictly aggregates/sums without integration.
     Examples: Collection, Group, Scattered Object