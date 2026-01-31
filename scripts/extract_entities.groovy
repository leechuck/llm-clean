@GrabResolver(name='central', root='https://repo1.maven.org/maven2/')
@Grapes([
    @Grab(group='net.sourceforge.owlapi', module='owlapi-distribution', version='5.5.0'),
    @Grab(group='org.slf4j', module='slf4j-simple', version='2.0.9'),
    @GrabExclude('commons-logging:commons-logging')
])

import org.semanticweb.owlapi.apibinding.OWLManager
import org.semanticweb.owlapi.model.*
import org.semanticweb.owlapi.search.EntitySearcher
import groovy.json.JsonBuilder

// Check args
if (args.length < 1) {
    System.err.println("Usage: groovy extract_entities.groovy <owl_file_path>")
    System.exit(1)
}

def owlFile = new File(args[0])
def manager = OWLManager.createOWLOntologyManager()
def ontology = manager.loadOntologyFromOntologyDocument(owlFile)
def df = manager.getOWLDataFactory()

def entities = []

ontology.getClassesInSignature().each { owlClass ->
    if (!owlClass.isOWLNothing() && !owlClass.isOWLThing()) {
        def term = owlClass.getIRI().getShortForm()
        def uri = owlClass.getIRI().toString()
        def description = ""

        // Try to get rdfs:label
        EntitySearcher.getAnnotations(owlClass, ontology, df.getRDFSLabel()).each { annotation ->
            if (annotation.getValue() instanceof OWLLiteral) {
                term = ((OWLLiteral) annotation.getValue()).getLiteral()
            }
        }

        // Try to get rdfs:comment
        EntitySearcher.getAnnotations(owlClass, ontology, df.getRDFSComment()).each { annotation ->
            if (annotation.getValue() instanceof OWLLiteral) {
                description = ((OWLLiteral) annotation.getValue()).getLiteral()
            }
        }

        entities << [
            term: term,
            uri: uri,
            description: description
        ]
    }
}

println(new JsonBuilder(entities).toPrettyString())
