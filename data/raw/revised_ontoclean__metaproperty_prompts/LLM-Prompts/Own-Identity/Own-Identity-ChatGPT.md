## +O — Supplies Its Own Identity Condition

Use **+O** when the property itself provides a basic identity rule for its instances.

In simpler terms:

 A **+O** property does not just describe a kind of thing; it tells the AI what counts as one individual thing of that kind.

### Examples

- **Person**  
  Supplies its own identity condition for deciding when someone is the same person over time.

- **Physical Object**  
  Supplies an identity condition based on physical or spatio-temporal continuity.

- **Organization**  
  May supply its own identity condition through legal, institutional, or structural continuity.


## -O — Does Not Supply Its Own Identity Condition

Use **-O** when the property does **not** introduce its own identity rule.

This can happen in two ways:

1. The property **inherits** an identity condition from a more general property.
2. The property has **no identity condition at all**.

In simpler terms:

 A **-O** property either borrows its identity rule from another class or does not provide any identity rule.

### Examples

- **Student**  
  Does not supply its own identity condition. A student is identified as the same individual because they are a **Person**.

- **Employee**  
  Usually inherits identity from **Person**, not from being an employee.

- **Red**  
  Does not supply an identity condition because it is a quality or attribute, not an individuating kind.

---

## Relationship Between Own Identity and Identity

Important rule:

 If a property is **+O**, then it must also be **+I**.

A property cannot supply its own identity condition unless it carries an identity condition in the first place.

### Possible combinations

| Identity | Own Identity | Meaning |
|---|---|---|
| **+I** | **+O** | The property carries and supplies its own identity condition. |
| **+I** | **-O** | The property carries identity, but inherits it from a parent class. |
| **-I** | **-O** | The property has no identity condition to supply. |
| **-I** | **+O** | Invalid combination. A property cannot supply identity if it does not carry identity. |

## Useful AI Decision Question

Ask:

 “Does this property itself define what counts as one and the same instance, or does it rely on a more general class for that?”

- If the property itself defines the identity rule, classify it as **+O**.
- If the identity rule comes from a parent class, classify it as **-O**.
- If there is no identity rule, classify it as **-O**.