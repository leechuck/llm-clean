#!/usr/bin/env python3
"""
Batch analyze entities from an OWL file using specialized agents with critic validation.
"""
import sys, os, pathlib
from git_root import git_root
sys.path.append(str(pathlib.Path(git_root())))

import argparse
import textwrap
import sys
import os
import json
import csv
from rdflib import Graph, RDF, OWL, RDFS
from src.llm_clean.ontology.agent_critic_analyzer import AgentCriticOntologyAnalyzer


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
        description="Batch analyze OWL entities using specialized agents with critic validation",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("input_owl", help="Path to the input OWL file.")
    parser.add_argument("--format", choices=["tsv", "json"], default="tsv",
                       help="Output format (tsv or json).")
    parser.add_argument("--output", help="Output file path (default: stdout).")
    parser.add_argument("--model",
                       default="gemini-3-flash-preview",
                       help=textwrap.dedent("""\
                            OpenRouter model ID.
                            Supported: google/gemini-3-flash-preview (default), anthropic/claude-4.5-sonnet.
                            You can also use 'gemini' or 'anthropic' as shortcuts."""))

    # Background file options
    parser.add_argument("--background-file", dest="background_file",
                       help=textwrap.dedent("""\
                            Default background file for all properties (.txt or .pdf).
                            Overrides default background type if provided.)"""))
    parser.add_argument("--no-default-backgrounds", dest="no_default_backgrounds",
                       action="store_true",
                       help=textwrap.dedent("""\
                            Disable default property-specific background files (default: disabled).
                            If set, the agent will use the hardcoded prompts without any additional background information."""))
    parser.add_argument("--default-background-file-type", dest="default_background_file_type",
                       choices=["augmented", "simple"], default="augmented",
                       help=textwrap.dedent("""\
                            Specifies a type of background files to use for properties.
                            Options are: "augmented", "simple".
                            "augmented":
                                    Uses the section of Guarino's paper defining each meta-property,
                                    but with the introduction added to each section.
                            "simple":
                                    Uses only the section of Guarino's paper defining each
                                    meta-property (without any augmentation).
                            "Default: "augmented"."""))

    # Critic-specific options
    parser.add_argument("--max-critique-attempts", dest="max_critique_attempts",
                       type=int, default=3,
                       help=textwrap.dedent("""\
                            Maximum number of critique/re-analysis attempts per property (default: 3).
                            If the critic rejects an analysis, the agent will re-analyze with feedback.
                            This parameter limits how many times this can happen before moving on."""))

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

    # Initialize analyzer with critic
    analyzer = None
    try:
        analyzer = AgentCriticOntologyAnalyzer(
            model=args.model,
            background_file=args.background_file if args.background_file else None,
            use_default_backgrounds=not args.no_default_backgrounds,
            default_background_file_type=args.default_background_file_type,
            max_critique_attempts=args.max_critique_attempts
        )
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    total = len(classes)
    print(f"Found {total} classes. Starting agent-based analysis with critic validation...", file=sys.stderr)

    for i, cls in enumerate(classes):
        term = cls['term']
        desc = cls['description']
        print(f"\n[{i+1}/{total}] Analyzing: {term}", file=sys.stderr)

        try:
            analysis = analyzer.analyze(term, description=desc)

            props = analysis.get("properties", {})
            reasoning = analysis.get("reasoning", {})
            critique_info = analysis.get("critique_info", {})

            # Show critique summary
            total_attempts = sum(critique_info.values())
            print(f"  Total critique attempts: {total_attempts}", file=sys.stderr)

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
                "dependence_reasoning": reasoning.get("dependence", ""),
                # Add critique attempt counts
                "rigidity_attempts": critique_info.get("rigidity_attempts", 0),
                "identity_attempts": critique_info.get("identity_attempts", 0),
                "own_identity_attempts": critique_info.get("own_identity_attempts", 0),
                "unity_attempts": critique_info.get("unity_attempts", 0),
                "dependence_attempts": critique_info.get("dependence_attempts", 0),
                "total_critique_attempts": total_attempts
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
                "rigidity_attempts",
                "identity_attempts",
                "own_identity_attempts",
                "unity_attempts",
                "dependence_attempts",
                "total_critique_attempts",
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
