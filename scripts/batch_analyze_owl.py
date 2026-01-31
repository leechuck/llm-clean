import argparse
import sys
import os
import json
import csv
from rdflib import Graph, RDF, OWL, RDFS

# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology_tools.analyzer import OntologyAnalyzer

def extract_classes(owl_path):
    g = Graph()
    g.parse(owl_path)
    
    classes = []
    for s, p, o in g.triples((None, RDF.type, OWL.Class)):
        # Extract label or use local name
        label = g.value(s, RDFS.label)
        if not label:
            # simple local name extraction from URI
            if "#" in str(s):
                label = str(s).split("#")[-1]
            else:
                label = str(s).split("/")[-1]
        
        # Extract comment/description if available
        comment = g.value(s, RDFS.comment)
        
        classes.append({
            "uri": str(s),
            "term": str(label),
            "description": str(comment) if comment else None
        })
    return classes

def main():
    parser = argparse.ArgumentParser(description="Batch analyze entities from an OWL file.")
    parser.add_argument("input_owl", help="Path to the input OWL file.")
    parser.add_argument("--format", choices=["tsv", "json"], default="tsv", help="Output format (tsv or json).")
    parser.add_argument("--output", help="Output file path (default: stdout).")
    parser.add_argument("--num-classes", type=int, help="Number of classes to analyze (None for all). Useful for testing.")
    parser.add_argument("--model",
                       default="gemini-3-flash-preview",
                       help="""
                                OpenRouter model ID. Supported: google/gemini-3-flash-preview (default), anthropic/claude-4.5-sonnet. \n
                                You can also use 'gemini' or 'anthropic' as shortcuts for the models.
                            """
                        )
    parser.add_argument("--background-file", dest="background_file",
                       help="Path to background information file (.txt or .pdf)")

    args = parser.parse_args()

    try:
        classes = extract_classes(args.input_owl)
    except Exception as e:
        print(f"Error loading OWL file: {e}", file=sys.stderr)
        sys.exit(1)

    analyzer = None
    try:
        analyzer = OntologyAnalyzer(model=args.model, background_file=args.background_file)
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    total = len(classes)
    print(f"Found {total} classes. Starting analysis...", file=sys.stderr)

    for i, cls in enumerate(classes):
        term = cls['term']
        desc = cls['description']
        print(f"[{i+1}/{total}] Analyzing: {term}", file=sys.stderr)
        
        try:
            # We pass term as both term and usage context contextually might be helpful, 
            # but here we rely on the term and potential description from OWL.
            analysis = analyzer.analyze(term, description=desc)
            
            props = analysis.get("properties", {})
            row = {
                "term": term,
                "uri": cls['uri'],
                "rigidity": props.get("rigidity", "N/A"),
                "identity": props.get("identity", "N/A"),
                "unity": props.get("unity", "N/A"),
                "dependence": props.get("dependence", "N/A"),
                "classification": analysis.get("classification", "N/A"),
                "reasoning": analysis.get("reasoning", "N/A")
            }
            results.append(row)

            # check if we should limit number of classes analyzed
            if args.num_classes and i > args.num_classes:
                break
            
        except Exception as e:
            print(f"Failed to analyze '{term}': {e}", file=sys.stderr)
            results.append({
                "term": term,
                "uri": cls['uri'],
                "error": str(e)
            })

    # Output
    if args.output:
        out_stream = open(args.output, 'w', newline='', encoding='utf-8')
    else:
        out_stream = sys.stdout

    try:
        if args.format == "json":
            json.dump(results, out_stream, indent=2)
        else:
            fieldnames = ["term", "uri", "rigidity", "identity", "unity", "dependence", "classification", "reasoning", "error"]
            writer = csv.DictWriter(out_stream, fieldnames=fieldnames, delimiter='\t', extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
    finally:
        if args.output:
            out_stream.close()

if __name__ == "__main__":
    main()
