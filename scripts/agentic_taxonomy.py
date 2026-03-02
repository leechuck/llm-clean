import os
import json
import argparse
import sys
from llm_clean.agents.workflow import OntoCleanWorkflow

def main():
    parser = argparse.ArgumentParser(description="Generate agentic taxonomy using OntoClean Critic.")
    parser.add_argument("input_file", help="Path to input dataset JSON")
    parser.add_argument("output_file", help="Path to output taxonomy JSON")
    parser.add_argument("--model", required=True, help="OpenRouter model ID")
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)

    with open(args.input_file, 'r') as f:
        data = json.load(f)
    
    datasets = data.get("datasets", [])
    workflow = OntoCleanWorkflow(args.model)
    results = []
    
    print(f"Starting agentic workflow using model: {args.model}")
    
    for dataset in datasets:
        domain = dataset.get("domain")
        terms = dataset.get("terms", [])
        if not terms and "dataset" in dataset:
            terms = [x["term"] for x in dataset["dataset"]]
            
        print(f"  Processing domain: {domain} ({len(terms)} terms)")
        taxonomy = workflow.process_domain(domain, terms)
        
        dataset_result = dataset.copy()
        dataset_result["taxonomy"] = taxonomy
        results.append(dataset_result)

        # Intermediate save
        final_output = {"model": args.model + "-agentic", "datasets": results}
        with open(args.output_file, 'w') as f:
            json.dump(final_output, f, indent=2)

    print(f"Done. Taxonomy saved to {args.output_file}")

if __name__ == "__main__":
    # Ensure src is in path if running from root
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    main()
