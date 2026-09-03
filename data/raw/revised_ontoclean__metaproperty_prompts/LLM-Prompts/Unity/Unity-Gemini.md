### Unity (U)

**Unity (U)** – Does this thing have clear boundaries that make it one complete, single object? 

*   **+U (Unified Whole)**: The object has specific boundaries and its parts are structured together. If you break it apart, it stops being that thing. You cannot simply merge two of them together to get one bigger version. 
    *   *Examples:* Person, Car, Dog. *(Half a car is not a car; two people glued together are not one person).*
*   **-U (Just Stuff / Unbound)**: The thing does not have built-in boundaries. You can easily divide it into smaller pieces, or merge it with more of the same stuff, and it is still the same kind of thing. 
    *   *Examples:* Water, Sand, Red Plastic. *(If you pour two cups of water together, it is still just "water").*
*   **~U (Collection / Group)**: The object is explicitly just a group or pile of other distinct things. It is defined by being a plurality rather than a single integrated structure.
    *   *Examples:* A flock (of birds), a pile (of rocks), a team (of people), a constellation.

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