# Identity — Carries an Identity Condition

This metaproperty asks whether a property or class gives a principled way to tell:

- when two instances are the **same individual**, and
- whether an instance remains the **same individual over time**.

A property **carries identity** if its instances can be counted, distinguished, and re-identified using some identity rule, either supplied by that property itself or inherited from a more general parent property.

## +I — Carries an Identity Condition

Use **+I** when being an instance of this property comes with a rule for deciding:

- whether two described things are actually the **same instance**, and
- whether something observed at different times is still the **same instance**.

In simpler terms:

A **+I** property tells the AI what counts as “one and the same thing” of that kind.

### Examples

- **Person**  
  There are criteria for deciding whether someone is the same person over time.

- **Physical Object**  
  Physical objects can often be re-identified through spatio-temporal continuity, persistence, or material/structural continuity.

- **Student**  
  A student may not supply its own identity condition, but it carries one because students are persons.

## -I — Does Not Carry an Identity Condition

Use **-I** when the property does **not** provide a principled rule for individuating or re-identifying its instances.

In simpler terms:

A **-I** property describes a feature, condition, quality, or classification, but it does not by itself tell the AI what counts as one individual instance of that thing.

### Examples

- **Red**  
  Redness is a quality. The property “red” does not tell us what counts as one individual red thing or the same red thing over time.

- **Tall**  
  Tallness describes a condition or quality, not an identity criterion.

- **Amount of Matter**  
  If modeled as undifferentiated stuff, such as water, clay, or sand, it may not provide a clear rule for what counts as one individual instance unless the ontology adds boundaries or identity criteria.


## Useful AI Decision Question

Ask:

> “If two things are both instances of this property, does the ontology or common meaning of the property provide a rule for deciding whether they are the same individual or two different individuals?”

- If **yes**, classify as **+I**.
- If **no**, classify as **-I**.

## Caution

**Recognizability is not the same as identity.**

The fact that we can detect, label, or describe something does not mean the property itself provides an identity condition.