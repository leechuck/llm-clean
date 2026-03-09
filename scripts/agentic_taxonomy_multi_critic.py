import os
import json
import argparse
import sys
from llm_clean.agents.multi_critic_workflow import MultiCriticWorkflow

def main():
    parser = argparse.ArgumentParser(description="Generate agentic taxonomy using Multi-Critic OntoClean workflow.")
    parser.add_argument("input_file", help="Path to input dataset JSON")
    parser.add_argument("output_file", help="Path to output taxonomy JSON")
    parser.add_argument("--model", required=True, help="OpenRouter model ID")
    parser.add_argument("--threshold", type=int, default=1,
                        help="Rejection threshold: how many critics must reject (default: 1 = any single critic)")
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)

    with open(args.input_file, 'r') as f:
        data = json.load(f)

    datasets = data.get("datasets", [])
    workflow = MultiCriticWorkflow(args.model, rejection_threshold=args.threshold)
    results = []

    # Resume support: load existing results if output file exists
    done_domains = set()
    if os.path.exists(args.output_file):
        with open(args.output_file, 'r') as f:
            existing = json.load(f)
        results = existing.get("datasets", [])
        done_domains = {ds["domain"] for ds in results}
        if done_domains:
            print(f"Resuming: {len(done_domains)} domains already complete, skipping them.")

    print(f"Starting multi-critic agentic workflow using model: {args.model} (threshold={args.threshold})")

    for dataset in datasets:
        domain = dataset.get("domain")
        terms = dataset.get("terms", [])
        if not terms and "dataset" in dataset:
            terms = [x["term"] for x in dataset["dataset"]]

        if domain in done_domains:
            print(f"  Skipping already-completed domain: {domain}")
            continue

        print(f"  Processing domain: {domain} ({len(terms)} terms)")
        taxonomy = workflow.process_domain(domain, terms)

        dataset_result = dataset.copy()
        dataset_result["taxonomy"] = taxonomy
        results.append(dataset_result)

        # Intermediate save
        suffix = f"-agentic-multi-critic-t{args.threshold}"
        final_output = {"model": args.model + suffix, "datasets": results}
        with open(args.output_file, 'w') as f:
            json.dump(final_output, f, indent=2)

    print(f"Done. Taxonomy saved to {args.output_file}")

if __name__ == "__main__":
    # Ensure src is in path if running from root
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    main()
