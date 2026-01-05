import argparse
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL

def generate_ontology(output_path):
    g = Graph()
    
    # Define Namespace
    EX = Namespace("http://example.org/guarino-messy#")
    g.bind("ex", EX)
    
    # Helper to add class
    def add_class(name, parents=None):
        cls = EX[name]
        g.add((cls, RDF.type, OWL.Class))
        if parents:
            if not isinstance(parents, list):
                parents = [parents]
            for p in parents:
                parent_cls = EX[p]
                g.add((cls, RDFS.subClassOf, parent_cls))
        return cls

    # Based on Figure 2 "A messy taxonomy" from Guarino & Welty (2000)
    
    # Root
    add_class("Entity")
    
    # Level 1
    add_class("Location", "Entity")
    add_class("AmountOfMatter", "Entity")
    add_class("Red", "Entity") # Attribute as Class
    add_class("Agent", "Entity")
    add_class("Group", "Entity")
    
    # Level 2 & Deeper (The Mess)
    
    # Under AmountOfMatter
    add_class("PhysicalObject", "AmountOfMatter")
    add_class("LivingBeing", "AmountOfMatter") # In messy taxonomies this often happens
    
    # Under PhysicalObject
    add_class("Fruit", "PhysicalObject")
    add_class("Food", "PhysicalObject") 
    
    # Apple is Fruit AND Food
    add_class("Apple", ["Fruit", "Food"])
    
    # RedApple is Apple AND Red
    add_class("RedApple", ["Apple", "Red"])
    
    # Under LivingBeing
    add_class("Animal", "LivingBeing")
    
    # Under Animal
    add_class("Vertebrate", "Animal")
    add_class("Caterpillar", "Animal")
    add_class("Butterfly", "Animal")
    
    # Under Group
    add_class("GroupOfPeople", "Group")
    add_class("SocialEntity", "Group")
    
    # Organization is SocialEntity AND LegalAgent?
    # Let's check Agent branch first
    add_class("LegalAgent", "Agent")
    
    # Organization
    add_class("Organization", ["SocialEntity", "LegalAgent"])
    
    # Person
    add_class("Person", ["Vertebrate", "LegalAgent"])
    
    # Country: The messy triple inheritance often cited
    # Location, SocialEntity (political), LegalAgent?
    # Figure 2 text dump shows connections to Location, Organization?? 
    # Let's stick to the common messy interpretation:
    add_class("Country", ["Location", "SocialEntity"]) # And sometimes Organization/LegalAgent implies SocialEntity

    print(f"Generating OWL ontology with {len(g)} triples...")
    g.serialize(destination=output_path, format="xml")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate the messy taxonomy OWL.")
    parser.add_argument("--output", required=True, help="Output OWL file path.")
    args = parser.parse_args()
    
    generate_ontology(args.output)
