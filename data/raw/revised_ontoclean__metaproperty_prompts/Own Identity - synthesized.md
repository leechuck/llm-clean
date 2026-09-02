# Instruction: Evaluating OntoClean's Own Identity (+O / -O) Metaproperty

Evaluate the **Own Identity** metaproperty by determining whether a concept is the **original source** of a global rule used to track and distinguish its instances, rather than inheriting that rule from a parent or relying on a temporary role. 

This metaproperty has three strict prerequisites. To be marked **+O**, a class must be:
1. **+I (Carries Identity):** It must have an answer to "same one or different one?"
2. **+R (Rigid):** The class must define what the entity essentially is. Non-rigid classes (temporary roles, phases) **cannot** supply identity. 
3. **An Originator/Augmentor:** It must introduce a fundamental tracking rule that is not entirely provided by its parent classes, or it must add a compatible, further criterion that its parents lack.

### +O (Supplies Its Own Identity Condition)
Assign **+O** if the class defines a **global** tracking rule that must hold throughout an instance's existence, and it is the origin point for that rule. 
*   **Augmentation:** A class is also +O if it inherits an identity condition from a +O parent but adds a *new, compatible* criterion on top of it.
*   *Examples:* Person (originates personal identity), Amount of Matter (originates mereological identity), Statue (originates sameness of form).

### -O (Does Not Supply Identity)
Assign **-O** if the class fails any of the three prerequisites. Record which of the following reasons applies:
*   **Not Rigid (-R or ~R):** The class represents a role or phase. *Even if it has a local identifier* (like a Student ID or Employee Number), these only track the entity during an episode and do not constitute a global identity condition. (e.g., Student, Employee, Passenger).
*   **Rigid, but Inherited:** The class is +I and +R, but it relies entirely on a parent class for its identity rule and adds nothing new. (e.g., *Mammal* relies entirely on *Organism*; *Integer* relies entirely on *Number*).
*   **No Identity (-I):** The class carries no identity condition to begin with. (e.g., Red, Entity, Large).