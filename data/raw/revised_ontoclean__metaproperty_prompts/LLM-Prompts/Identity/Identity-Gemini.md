### Identity (I)

**Identity (I)** – Does this concept give you a rule to uniquely tell apart two things, or to recognize the *exact same* thing again later?

*   **+I (Identifiable / Trackable)**: Yes. If something is an instance of this concept, there is a clear way to distinguish it from others of its kind, and track it as the exact same individual over time. It has unique, recognizable fingerprints (literal or metaphorical).
    *   *Examples:* Person (distinguished by DNA, memory, or physical continuity), Car (distinguished by a VIN or continuous physical structure), Bank Account (distinguished by an account number).
*   **-I (Untrackable / Generic Trait or Stuff)**: No. The concept itself provides no rule for telling instances apart or tracking them. These are usually descriptions, colors, materials, or measurements that only exist *on* or *in* other objects.
    *   *Examples:* Red (you cannot track "the exact same redness" independent of the red object), Heavy, Amount of Clay (you cannot distinguish one "amount" from another once they are mixed).

To help the AI agent accurately classify this property, you can include these simple true/false questions in its prompt:

**The "Same One" Test (Re-identification):**
*   If I see an instance of this today, and an instance tomorrow, is there a factual way to prove they are the *exact same* individual, rather than just two identical-looking copies?
    *   *If YES* $\rightarrow$ likely **+I** (I can prove this is the exact same dog using its microchip).
    *   *If NO* $\rightarrow$ likely **-I** (I cannot prove this is the exact same "redness" or "amount of water" without referring to the cup or the car it belongs to).

**The "Distinction" Test:**
*   If there are two of these right next to each other, is there a built-in rule to explain why there are two instead of one?
    *   *If YES* $\rightarrow$ likely **+I** (Two people have two distinct bodies/minds).
    *   *If NO* $\rightarrow$ likely **-I** (Two instances of "red" next to each other just blend into a larger area of red).