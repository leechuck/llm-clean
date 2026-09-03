# Instruction: Evaluating OntoClean's Dependence (D) Metaproperty

Evaluate the **Dependence** metaproperty by determining if a concept exhibits **external, existential dependence**. This is a strict dichotomy with only two valid labels: **+D** and **-D**.

### +D (Externally Dependent)
Assign **+D** if every instance of the property logically requires some **other, separate** entity to exist alongside it in order to be an instance of that property. 
*   **Generic Requirement:** The instance requires *some* external entity of a specific kind, though the exact individual counterpart may change (e.g., a student needs *some* school).
*   **Strict Exclusion:** The required entity must be truly external. It **cannot** be a part of the instance, its constituent matter, a member of a collection, or a causal background condition (like sunlight, gravity, or spacetime). 
*   *Examples:* Student (requires an educational institution), Hole (requires a host object), Husband (requires a spouse).

### -D (Independent)
Assign **-D** if instances of the property can logically exist completely on their own without requiring any separate, external entity as part of their definition.
*   *Examples:* Person (internal organs are parts, not external dependencies), Rock, Physical Object, Team (members are excluded from being external dependencies).