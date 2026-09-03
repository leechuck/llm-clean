# ChatGPT-5-5 Pro 5 (2026-09-01)

# Unity — Instances Are Integrated Wholes

This metaproperty asks whether instances of a property or class are normally understood as **single, integrated wholes**, rather than loose collections, arbitrary sums, or scattered parts.

A property has **Unity** when its instances have parts that belong together because of some organizing principle, such as biological function, physical structure, functional design, social organization, or institutional structure.

---

## +U — Unifying

Use **+U** when every instance of the property is expected to be a genuine whole whose parts are connected or organized in a principled way.

In simpler terms:

> A **+U** property describes things whose parts belong together as one integrated unit.

### Examples

- **Person**  
  A person is a biological whole. Organs, tissues, and body parts are integrated into one living organism.

- **Car**  
  A car is a functional whole. Its parts are arranged and connected to work together as a vehicle.

- **House**  
  A house is a structural and functional whole. Walls, roof, rooms, and systems are organized as one building.

---

## -U — Non-Unifying

Use **-U** when the property does not guarantee that its instances are integrated wholes.

The property may apply to things that are wholes, but it does not itself explain what makes them whole.

In simpler terms:

> A **-U** property does not tell the AI whether its instances are single integrated objects or arbitrary things.

### Examples

- **Red Thing**  
  Something red could be a whole object, like a red apple, or an arbitrary collection of red objects. The property “red” does not make something a unified whole.

- **Amount of Water**  
  Water may be in one glass, spread across several containers, or scattered as droplets. Being water does not by itself provide unity.

- **Physical Thing**  
  Depending on the ontology, this may include both integrated objects and arbitrary physical sums, so it may not supply a single unity rule.

---

## ~U — Anti-Unity

Use **~U** when instances are, by definition, not integrated wholes.

These instances are aggregates, collections, sums, or scattered pluralities whose parts are grouped together without forming one unified object.

In simpler terms:

> A **~U** property describes things that are necessarily mere groupings or aggregates, not true integrated wholes.

### Examples

- **Collection**  
  A collection is made of members grouped together, but the members do not necessarily form one integrated whole.

- **Group**  
  If modeled as a mere grouping of people or things, a group is not an integrated object in the same way a person or car is.

- **Scattered Object**  
  A scattered object is explicitly composed of separated parts that do not form one continuous or integrated whole.

- **Aggregate**  
  An aggregate is a sum of parts considered together without requiring internal organization.

---

## Difference Between -U and ~U

| Unity Value | Meaning | Simple Test |
|---|---|---|
| **+U** | Instances must be integrated wholes. | The parts belong together as one unit. |
| **-U** | The property does not say whether instances are wholes. | Some instances may be wholes, but unity is not guaranteed. |
| **~U** | Instances are necessarily not integrated wholes. | The instance is only a collection, sum, or aggregate. |

---

## Short Prompt-Ready Version

> Mark a property as **+U** if every instance must be a single integrated whole whose parts belong together under some organizing principle. Mark it as **-U** if the property does not determine whether its instances are unified wholes. Mark it as **~U** if every instance is necessarily an aggregate, collection, scattered sum, or plurality rather than an integrated whole.

---

## Useful AI Decision Questions

Ask:

> “Does this property require each instance to be one integrated whole?”

- If **yes**, classify it as **+U**.
- If **no**, ask the next question.

Then ask:

> “Are instances of this property necessarily mere collections, aggregates, sums, or scattered pluralities?”

- If **yes**, classify it as **~U**.
- If **no**, classify it as **-U**.

---

## Cautions

- **Unity is not the same as identity.**  
  Identity asks what makes something the same individual over time. Unity asks whether its parts form one integrated whole.

- **Touching is not always unity.**  
  A pile of rocks may be physically touching, but that does not necessarily make it a unified object.

- **Collections and groups depend on modeling choices.**  
  A casual collection is usually **~U**, but an organization or institution may be modeled as **+U** if it has internal structure and continuity.