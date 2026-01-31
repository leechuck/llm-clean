#!/usr/bin/env python3
"""
Batch analyze entities from an OWL file using specialized agents for each meta-property.
"""
import argparse
import sys
import os
import json
import csv
from rdflib import Graph, RDF, OWL, RDFS

# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology_tools.agent_analyzer import AgentOntologyAnalyzer


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
    parser = argparse.ArgumentParser(
        description="Batch analyze OWL entities using specialized agents for each meta-property"
    )
    parser.add_argument("input_owl", help="Path to the input OWL file.")
    parser.add_argument("--format", choices=["tsv", "json"], default="tsv",
                       help="Output format (tsv or json).")
    parser.add_argument("--output", help="Output file path (default: stdout).")
    parser.add_argument("--model",
                       default="gemini-3-flash-preview",
                       help="OpenRouter model ID. Supported: google/gemini-3-flash-preview (default), "
                            "anthropic/claude-4.5-sonnet. You can also use 'gemini' or 'anthropic' as shortcuts.")

    # Background file options
    parser.add_argument("--default-background", dest="default_background",
                       help="Default background file for all properties (.txt or .pdf). "
                            "Overrides property-specific defaults if provided.")
    parser.add_argument("--no-default-backgrounds", dest="no_default_backgrounds",
                       action="store_true",
                       help="Disable default property-specific background files")
    parser.add_argument("--rigidity-background", dest="rigidity_background",
                       help="Background file specifically for Rigidity analysis")
    parser.add_argument("--identity-background", dest="identity_background",
                       help="Background file specifically for Identity analysis")
    parser.add_argument("--own-identity-background", dest="own_identity_background",
                       help="Background file specifically for Own Identity analysis")
    parser.add_argument("--unity-background", dest="unity_background",
                       help="Background file specifically for Unity analysis")
    parser.add_argument("--dependence-background", dest="dependence_background",
                       help="Background file specifically for Dependence analysis")

    parser.add_argument("--limit", type=int,
                       help="Limit number of entities to analyze (for testing)")

    args = parser.parse_args()

    try:
        classes = extract_classes(args.input_owl)
    except Exception as e:
        print(f"Error loading OWL file: {e}", file=sys.stderr)
        sys.exit(1)

    if args.limit:
        classes = classes[:args.limit]
        print(f"Limiting analysis to first {args.limit} classes", file=sys.stderr)

    # Build background_files dict
    background_files = {}
    if args.rigidity_background:
        background_files['rigidity'] = args.rigidity_background
    if args.identity_background:
        background_files['identity'] = args.identity_background
    if args.own_identity_background:
        background_files['own_identity'] = args.own_identity_background
    if args.unity_background:
        background_files['unity'] = args.unity_background
    if args.dependence_background:
        background_files['dependence'] = args.dependence_background

    # Initialize analyzer
    analyzer = None
    try:
        analyzer = AgentOntologyAnalyzer(
            model=args.model,
            background_files=background_files if background_files else None,
            default_background_file=args.default_background,
            use_default_backgrounds=not args.no_default_backgrounds
        )
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    total = len(classes)
    print(f"Found {total} classes. Starting agent-based analysis...", file=sys.stderr)

    for i, cls in enumerate(classes):
        term = cls['term']
        desc = cls['description']
        print(f"\n[{i+1}/{total}] Analyzing: {term}", file=sys.stderr)

        try:
            analysis = analyzer.analyze(term, description=desc)

            props = analysis.get("properties", {})
            reasoning = analysis.get("reasoning", {})

            row = {
                "term": term,
                "uri": cls['uri'],
                "rigidity": props.get("rigidity", "N/A"),
                "identity": props.get("identity", "N/A"),
                "own_identity": props.get("own_identity", "N/A"),
                "unity": props.get("unity", "N/A"),
                "dependence": props.get("dependence", "N/A"),
                "classification": analysis.get("classification", "N/A"),
                "rigidity_reasoning": reasoning.get("rigidity", ""),
                "identity_reasoning": reasoning.get("identity", ""),
                "own_identity_reasoning": reasoning.get("own_identity", ""),
                "unity_reasoning": reasoning.get("unity", ""),
                "dependence_reasoning": reasoning.get("dependence", "")
            }
            results.append(row)

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
            fieldnames = [
                "term", 
                "uri",
                "rigidity", 
                "identity", 
                "own_identity", 
                "unity", 
                "dependence", 
                "classification", 
                "rigidity_reasoning",
                "identity_reasoning",
                "own_identity_reasoning",
                "unity_reasoning",
                "dependence_reasoning",
                "error"
            ]
            writer = csv.DictWriter(out_stream, fieldnames=fieldnames, delimiter='\t',
                                   extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
    finally:
        if args.output:
            out_stream.close()
            print(f"\nResults written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
