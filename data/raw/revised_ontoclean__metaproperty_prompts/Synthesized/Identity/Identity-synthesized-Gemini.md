# Instruction: Evaluating OntoClean's Identity (I) Metaproperty

Evaluate the **Identity** metaproperty by determining if a concept provides or inherits a principled rule to individuate, count, and track its instances over time. 

### +I (Carries an Identity Condition)
Assign **+I** if *being that kind of thing* provides a rule for determining what counts as one and the same individual. It allows you to answer whether two given instances are the same entity, and whether an instance remains the exact same individual through changes over time. 
*   **Inheritance:** Identity conditions are inherited downward. If a class (e.g., *Student*) does not supply its own rule but is subsumed by a parent class that does (e.g., *Person*), it inherits that condition and must be marked **+I**.
*   *Note on Identifiers:* Do not confuse identity with having a primary key or label (like a fingerprint or VIN). Identity is about what ontologically makes it the same entity, not how we happen to look it up.
*   *Examples:* Person, Physical Object, Student, Event, Amount of Matter (same matter = same amount).

### -I (Does Not Carry an Identity Condition)
Assign **-I** if the property supplies no rule for counting, distinguishing, or re-identifying instances. These are typically qualities, states, or highly abstract top-level categories where you cannot meaningfully ask "how many?" without first borrowing a different noun to do the counting (e.g., you cannot count "reds," only red *things*).
*   *Examples:* Red, Large, Damaged, Entity, Thing.