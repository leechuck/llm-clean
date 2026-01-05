import argparse
import sys
import os
import json
import csv
import subprocess

# Ensure the project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology_tools.analyzer import OntologyAnalyzer

def get_entities_from_groovy(owl_path):
    groovy_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extract_entities.groovy")
    
    # Run groovy script
    # Assumes 'groovy' is in PATH. If not, this needs adjustment.
    cmd = ["groovy", groovy_script, owl_path]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Groovy script execution failed: {e.stderr}", file=sys.stderr)
        raise
    except json.JSONDecodeError as e:
        print(f"Failed to parse Groovy output as JSON: {e}", file=sys.stderr)
        print(f"Groovy STDOUT: {result.stdout}", file=sys.stderr)
        raise

def main():
    parser = argparse.ArgumentParser(description="Batch analyze entities from an OWL file using OWLAPI (via Groovy).")
    parser.add_argument("input_owl", help="Path to the input OWL file.")
    parser.add_argument("--format", choices=["tsv", "json"], default="tsv", help="Output format (tsv or json).")
    parser.add_argument("--output", help="Output file path (default: stdout).")
    parser.add_argument("--model", default="openai/gpt-4o", help="OpenRouter model ID.")
    
    args = parser.parse_args()
    
    print("Extracting entities using Groovy/OWLAPI...", file=sys.stderr)
    try:
        classes = get_entities_from_groovy(args.input_owl)
    except Exception as e:
        print(f"Error extracting entities: {e}", file=sys.stderr)
        sys.exit(1)
        
    analyzer = None
    try:
        analyzer = OntologyAnalyzer(model=args.model)
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
