# ChatGPT-5-5 Pro 5 (2026-09-01)

# Dependence — Requires Another Entity

This metaproperty asks whether instances of a property or class **must depend on some other distinct entity** in order to exist as instances of that property.

A property is dependent when being that kind of thing necessarily involves another entity, such as a host, owner, institution, bearer, object, participant, or context.

---

## +D — Dependent

Use **+D** when every instance of the property must depend on some other entity.

In simpler terms:

> A **+D** property describes things that cannot exist as that kind of thing unless some other required entity also exists or is involved.

The dependency may be on:

- a **specific individual**, such as a particular host or owner, or
- some entity of a **required type**, such as some school, employer, host, or bearer.

### Examples

- **Student**  
  A student depends on an educational institution, course, program, or educational context.  
  A person can exist without being a student, but cannot be a student without some educational setting.

- **Employee**  
  An employee depends on an employer or employing organization.

- **Parasite**  
  A parasite depends on a host, or on hosts as part of its life process.

- **Hole**  
  A hole depends on the physical object or material in which the hole exists.

- **Color Quality**  
  A particular color instance depends on something that has that color.

---

## -D — Independent

Use **-D** when instances of the property can exist without necessarily depending on another specific kind of entity.

In simpler terms:

> A **-D** property describes things that can exist on their own, without requiring another external entity as part of what they are.

### Examples

- **Person**  
  A person may need food, air, and social support in practice, but being a person does not require dependence on one specific external entity.

- **Physical Object**  
  A physical object can exist without being defined by a necessary relationship to another object.

- **Rock**  
  A rock does not need an owner, host, institution, or bearer in order to be a rock.

- **Tree**  
  A tree has environmental needs, but it is not defined by dependence on one required external entity.

---

## Difference Between Practical Need and Ontological Dependence

Dependence is not just about needing something in an ordinary practical sense.

For example:

- A person needs oxygen to survive, but **Person** is usually not treated as **+D**.
- A student needs an educational institution or educational context to be a student, so **Student** is **+D**.
- A painting may need paint to be made, but that historical fact does not automatically make **Painting** dependent in the OntoClean sense.

Ontological dependence asks whether the relationship to another entity is part of what makes something an instance of the property.

---

## Short Prompt-Ready Version

> Mark a property as **+D** if every instance must depend on some other distinct entity in order to exist as an instance of that property. Mark it as **-D** if instances can exist without any required external entity being part of their definition.

---

## Useful AI Decision Questions

Ask:

> “Can something be an instance of this property without some other required entity existing or being involved?”

- If **no**, classify it as **+D**.
- If **yes**, classify it as **-D**.

Also ask:

> “If the related entity disappeared or did not exist, would the instance stop being this kind of thing?”

- If **yes**, this suggests **+D**.
- If **no**, this suggests **-D**.

---

## Cautions

- **Dependence is not the same as causation.**  
  Something may have been caused or created by another entity without depending on it now.

- **Dependence is not the same as survival need.**  
  Living things need food, water, and air, but this does not automatically make them ontologically dependent.

- **Dependence usually concerns an external entity.**  
  Do not mark something as **+D** merely because it has internal parts.

- **Roles are often dependent.**  
  Classes like **Student**, **Employee**, **Customer**, **Tenant**, and **Patient** often depend on institutions, organizations, relationships, or contexts.

- **Independent does not mean isolated.**  
  A **-D** entity may still interact with many other entities; it just is not defined by a necessary dependence on them.