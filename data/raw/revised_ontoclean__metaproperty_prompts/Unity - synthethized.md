# Instruction: Evaluating OntoClean's Unity (U) Metaproperty

Evaluate the **Unity** metaproperty by determining if a concept supplies a principled criterion that dictates exactly which parts belong to an instance and where its boundaries lie. Unity is about having a non-arbitrary boundary at a given moment in time, not about internal complexity or whether parts are physically touching.

*Important Convention:* Always report the **strongest** true value. `~U` entails `-U`; if a class is anti-unified, it must be labeled `~U`.

### +U (Carries Unity)
Assign **+U** if all instances are genuine wholes bound by a **single, shared criterion**. The criterion may be topological (physical connection), morphological (shape/form), functional (working together for a purpose), biological, or social/intentional (rules of membership).
*   *Note on Groups/Collections:* A group with principled membership rules (like a team or string quartet) is **+U** (social unity). Do not automatically mark groups as `~U`.
*   *Examples:* Person (biological), Car (functional), Statue (morphological), Committee (social).

### ~U (Anti-Unity)
Assign **~U** if every instance is arbitrarily demarcated and completely lacks a principled boundary. For these concepts, you can arbitrarily add or remove bits of the instance and the result remains a perfectly valid instance of the exact same kind without being "damaged" or "incomplete."
*   *Examples:* Amount of Water, Amount of Matter, Sand, Arbitrary Spatial Region. 

### -U (Does Not Carry Unity)
Assign **-U** for the mixed case where the class fails to supply a *common* unifying criterion for all its instances. The instances may each be perfectly good wholes, but they are unified by entirely different criteria, meaning the class itself cuts across different kinds of unity.
*   *Examples:* Legal Agent (subsumes both biological *Persons* and social *Corporations*), Red Thing (a red car has functional unity, a red apple has biological unity; the class "Red Thing" supplies no shared boundary rule).