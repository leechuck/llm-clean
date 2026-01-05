import argparse
import csv
import sys
import os

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
    
    args = parser.parse_args()
    
    predictions = load_tsv(args.prediction_file)
    ground_truth = load_tsv(args.ground_truth_file)
    
    properties = ["rigidity", "identity", "own_identity", "unity", "dependence"]
    metrics = {prop: 0 for prop in properties}
    metrics["exact_match"] = 0
    
    count = 0
    
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
        for prop in properties:
            p_val = normalize_property(pred_row.get(prop))
            g_val = normalize_property(gt_row.get(prop))
            
            # Simple exact match
            match = (p_val == g_val)
            if match:
                metrics[prop] += 1
            else:
                row_correct = False
                print(f"{term:<20} {prop:<15} {p_val:<5} {g_val:<5} FAIL")
        
        if row_correct:
            metrics["exact_match"] += 1
    
    print("-" * 65)
    print("Evaluation Results:")
    if count == 0:
        print("No overlapping terms found.")
    else:
        print(f"Total Evaluated: {count}")
        for prop in properties:
             print(f"{prop.capitalize().replace('_', ' '):<15}: {metrics[prop]}/{count} ({metrics[prop]/count:.2%})")
        print(f"{ 'Exact Match':<15}: {metrics['exact_match']}/{count} ({metrics['exact_match']/count:.2%})")

if __name__ == "__main__":
    main()