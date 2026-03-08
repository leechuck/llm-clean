import argparse
import csv
import sys
import os
import json

def normalize_property(prop):
    """Normalize property strings (e.g., handles whitespace)."""
    if not prop:
        return "N/A"
    return prop.strip()

def load_tsv(path):
    data = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                term = row.get('term')
                if term:
                    data[term] = row
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    return data

def main():
    parser = argparse.ArgumentParser(description="Evaluate ontological analysis against ground truth.")
    parser.add_argument("prediction_file", help="Path to the prediction TSV file.")
    parser.add_argument("ground_truth_file", help="Path to the ground truth TSV file.")
    parser.add_argument("--output", "-o", help="Path to save evaluation results as JSON file.")
    parser.add_argument('--agent-name',help="Adds an 'agent_name' column to the output with the specified value (optional)")


    args = parser.parse_args()
    
    predictions = load_tsv(args.prediction_file)
    ground_truth = load_tsv(args.ground_truth_file)

    meta_properties = ["rigidity", "identity", "own_identity", "unity", "dependence"]
    metrics = {prop: 0 for prop in meta_properties}
    metrics["exact_match"] = 0

    count = 0
    detailed_results = []

    print(f"{ 'Term':<20} { 'Prop':<15} { 'Pred':<5} { 'Truth':<5} {'Result'}")
    print("-" * 65)

    for term, gt_row in ground_truth.items():
        if term not in predictions:
            continue

        pred_row = predictions[term]

        # Check for error in prediction
        if pred_row.get('error'):
            continue

        count += 1

        row_correct = True
        term_result = {
            "term": term,
            "exact_match": False,
            "properties": {}
        }

        for prop in meta_properties:
            p_val = normalize_property(pred_row.get(prop))
            g_val = normalize_property(gt_row.get(prop))

            # Simple exact match
            match = (p_val == g_val)
            term_result["properties"][prop] = {
                "predicted": p_val,
                "ground_truth": g_val,
                "match": match
            }

            if match:
                metrics[prop] += 1
            else:
                row_correct = False
                print(f"{term:<20} {prop:<15} {p_val:<5} {g_val:<5} FAIL")

        if row_correct:
            metrics["exact_match"] += 1
            term_result["exact_match"] = True
        
        if 'total_critique_attempts' in pred_row.keys():
            term_result['total_critique_attempts'] = int(pred_row['total_critique_attempts'])

        detailed_results.append(term_result)

    # check if total critique attempts is being tracked
    # if so, calculate average number of critique attempts across all terms and include in output
    ave_critique_attempts = 0
    if 'total_critique_attempts' in detailed_results[0].keys():
         number_of_terms = len(detailed_results)
         critique_attempts_count = sum([pred['total_critique_attempts'] for pred in detailed_results])
         ave_critique_attempts = round(critique_attempts_count / number_of_terms, 2)    
    
    print("-" * 65)
    print("Evaluation Results:")
    if count == 0:
        print("No overlapping terms found.")
    else:
        print(f"Total Evaluated: {count}")

        # check if agent name is provided and print it if so
        if args.agent_name:
            print(f"Agent Name: {args.agent_name}")

        for prop in meta_properties:
             print(f"{prop.capitalize().replace('_', ' '):<15}: {metrics[prop]}/{count} ({metrics[prop]/count:.2%})")
        print(f"{ 'Exact Match':<15}: {metrics['exact_match']}/{count} ({metrics['exact_match']/count:.2%})")

        if ave_critique_attempts > 0:
            print(f"{ 'Avg Critique Attempts':<15}: {ave_critique_attempts} per term")

        # Save to JSON if output file is specified
        if args.output:
            output_data = {
                "evaluation_summary": {
                    "total_evaluated": count,
                    "metrics": {
                        prop: f"{metrics[prop]}/{count} ({metrics[prop]/count:.2%})"
                        for prop in meta_properties
                    },
                    # "exact_match": f"{metrics['exact_match']}/{count} ({metrics['exact_match']/count:.2%})"
                },
                "detailed_results": detailed_results
            }
            output_data["evaluation_summary"]["metrics"]["exact_match"] = f"{metrics['exact_match']}/{count} ({metrics['exact_match']/count:.2%})"
            
            # check if total critique attempts is being tracked and add average to output if so
            if ave_critique_attempts > 0:
                output_data["evaluation_summary"]["metrics"]["ave_critique_attempts"] = ave_critique_attempts

            # check if agent name is provided and add it to the output data if so
            if args.agent_name:
                output_data["evaluation_summary"]["metrics"]["agent_name"] = args.agent_name

            # keep the old format for reference, but we will use the new format with summary strings for easier reporting
            # output_data = {
            #     "evaluation_summary": {
            #         "total_evaluated": count,
            #         "metrics": {
            #             prop: {
            #                 "correct": metrics[prop],
            #                 "total": count,
            #                 "accuracy": round(metrics[prop] / count, 2) if count > 0 else 0
            #             }
            #             for prop in properties
            #         },
            #         "exact_match": {
            #             "correct": metrics["exact_match"],
            #             "total": count,
            #             "accuracy": round(metrics["exact_match"] / count, 2) if count > 0 else 0
            #         }
            #     },
            #     "detailed_results": detailed_results
            # }

            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()