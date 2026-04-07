/**
 * extract_ncit_top.groovy
 *
 * Extracts the top-N classes (BFS-shallowest from owl:Thing) of a large
 * OWL ontology such as the NCI Thesaurus into the same TSV schema used by
 * the OntoClean inference pipeline:
 *
 *   uri  label  definition  parent_label
 *
 * Uses asserted (not inferred) direct subclass axioms — no reasoner — to
 * keep memory and runtime manageable on multi-hundred-MB ontologies.
 *
 * Usage:
 *   JAVA_OPTS="-Xmx16g" groovy scripts/extract_ncit_top.groovy \
 *       ontology/Thesaurus.owl 300 output/ncit_top300_entities.tsv
 */

@GrabResolver(name='central', root='https://repo1.maven.org/maven2/')
@Grapes([
    @Grab(group='net.sourceforge.owlapi', module='owlapi-distribution', version='5.5.0'),
    @Grab(group='org.slf4j',              module='slf4j-simple',        version='2.0.9'),
    @GrabExclude('commons-logging:commons-logging')
])

import org.semanticweb.owlapi.apibinding.OWLManager
import org.semanticweb.owlapi.model.*
import org.semanticweb.owlapi.model.parameters.Imports
import org.semanticweb.owlapi.search.EntitySearcher

if (args.length < 2) {
    System.err.println("Usage: groovy extract_ncit_top.groovy <owl_file> <N> [output.tsv]")
    System.exit(1)
}
def owlPath    = args[0]
def topN       = args[1] as int
def outputPath = args.length > 2 ? args[2] : null

System.err.println("[INFO] Loading ${owlPath} ...")
def manager  = OWLManager.createOWLOntologyManager()
def ontology = manager.loadOntologyFromOntologyDocument(new File(owlPath))
def df       = manager.getOWLDataFactory()
System.err.println("[INFO] Loaded: ${ontology.getOntologyID()}")
System.err.println("[INFO] Classes in signature: ${ontology.getClassesInSignature(Imports.INCLUDED).size()}")

// ── NCIt + IAO annotation properties ─────────────────────────────────────────
def IAO_DEF = df.getOWLAnnotationProperty(IRI.create("http://purl.obolibrary.org/obo/IAO_0000115"))
def NCIT_P97  = df.getOWLAnnotationProperty(IRI.create("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#P97"))   // DEFINITION
def NCIT_P108 = df.getOWLAnnotationProperty(IRI.create("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#P108"))  // preferred name

def getLiteral = { OWLEntity entity, OWLAnnotationProperty prop ->
    def result = ""
    EntitySearcher.getAnnotations(entity, ontology, prop).each { ann ->
        if (ann.getValue() instanceof OWLLiteral) {
            def lit = (OWLLiteral) ann.getValue()
            if (!result && lit.getLang() in ["en", ""]) result = lit.getLiteral()
        }
    }
    if (!result) {
        EntitySearcher.getAnnotations(entity, ontology, prop).each { ann ->
            if (ann.getValue() instanceof OWLLiteral)
                result = ((OWLLiteral) ann.getValue()).getLiteral()
        }
    }
    result
}

def getLabel = { OWLClass cls ->
    def lbl = getLiteral(cls, df.getRDFSLabel())
    if (!lbl) lbl = getLiteral(cls, NCIT_P108)
    lbl ?: cls.getIRI().getShortForm()
}

def getDefinition = { OWLClass cls ->
    def d = getLiteral(cls, IAO_DEF)
    if (!d) d = getLiteral(cls, NCIT_P97)
    if (!d) d = getLiteral(cls, df.getRDFSComment())
    // NCIt P97 definitions can be wrapped as XML literals; strip <def-source> tail
    if (d && d.contains("<def-source>")) d = d.substring(0, d.indexOf("<def-source>")).trim()
    if (d && d.startsWith("<def-definition>")) d = d.substring("<def-definition>".length(), d.indexOf("</def-definition>")).trim()
    d ?: ""
}

// ── Build asserted subclass index: parent -> [direct named children] ─────────
System.err.println("[INFO] Indexing direct subclass axioms ...")
def childrenOf = [:].withDefault { [] as Set }
ontology.getAxioms(AxiomType.SUBCLASS_OF, Imports.INCLUDED).each { OWLSubClassOfAxiom ax ->
    def sub = ax.getSubClass()
    def sup = ax.getSuperClass()
    if (sub instanceof OWLClass && sup instanceof OWLClass) {
        def subC = (OWLClass) sub
        def supC = (OWLClass) sup
        if (!subC.isOWLNothing() && !supC.isOWLNothing())
            childrenOf[supC] << subC
    }
}
System.err.println("[INFO] Indexed ${childrenOf.size()} parent classes with named children.")

// ── Find roots (named children of owl:Thing) ─────────────────────────────────
def thing = df.getOWLThing()
def roots = childrenOf[thing] as List
// classes with no asserted superclass (other than owl:Thing) also count as roots
def hasNamedSuper = [:].withDefault { false }
ontology.getAxioms(AxiomType.SUBCLASS_OF, Imports.INCLUDED).each { OWLSubClassOfAxiom ax ->
    if (ax.getSubClass() instanceof OWLClass && ax.getSuperClass() instanceof OWLClass) {
        def supC = (OWLClass) ax.getSuperClass()
        if (!supC.isOWLThing())
            hasNamedSuper[(OWLClass) ax.getSubClass()] = true
    }
}
ontology.getClassesInSignature(Imports.INCLUDED).each { OWLClass c ->
    if (!c.isOWLThing() && !c.isOWLNothing() && !hasNamedSuper[c] && !roots.contains(c))
        roots << c
}
System.err.println("[INFO] Root classes (direct named children of owl:Thing or unanchored): ${roots.size()}")

// ── BFS until we have N classes ──────────────────────────────────────────────
def visited = new LinkedHashSet<OWLClass>()
def queue = new ArrayDeque<OWLClass>()
roots.sort { getLabel(it) }
roots.each { queue << it; visited << it }

while (!queue.isEmpty() && visited.size() < topN) {
    def cur = queue.poll()
    def kids = (childrenOf[cur] as List).sort { getLabel(it) }
    for (k in kids) {
        if (visited.size() >= topN) break
        if (!visited.contains(k)) {
            visited << k
            queue << k
        }
    }
}
System.err.println("[INFO] Selected ${visited.size()} classes via BFS.")

// ── Build (sub -> first parent) map for parent_label ────────────────────────
def primaryParent = [:]
visited.each { OWLClass c ->
    def supers = []
    ontology.getAxioms(AxiomType.SUBCLASS_OF, Imports.INCLUDED).findAll { it.getSubClass() == c }.each { ax ->
        if (ax.getSuperClass() instanceof OWLClass) {
            def sc = (OWLClass) ax.getSuperClass()
            if (!sc.isOWLThing()) supers << sc
        }
    }
    primaryParent[c] = supers ? supers.first() : null
}

// ── Emit TSV ─────────────────────────────────────────────────────────────────
def clean  = { String s -> (s ?: "").replace('\t',' ').replace('\n',' ').replace('\r',' ') }
def header = "uri\tlabel\tdefinition\tparent_label"
def lines  = []
visited.each { OWLClass c ->
    def parent = primaryParent[c]
    def parentLabel = parent ? getLabel(parent) : ""
    lines << "${clean(c.getIRI().toString())}\t${clean(getLabel(c))}\t${clean(getDefinition(c))}\t${clean(parentLabel)}"
}

if (outputPath) {
    new File(outputPath).text = ([header] + lines).join('\n') + '\n'
    System.err.println("[INFO] Wrote ${visited.size()} rows to ${outputPath}")
} else {
    println header
    lines.each { println it }
}
