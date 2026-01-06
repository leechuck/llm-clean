import json
import csv
import sys
import os

def main():
    # Adjust paths relative to script location
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "results", "experiment_results.json")
    tsv_path = os.path.join(base_dir, "results", "experiment_results.tsv")
    
    if not os.path.exists(json_path):
        print(f"No results found at {json_path}")
        return

    with open(json_path, 'r') as f:
        results = json.load(f)

    rows = []
    
    for item in results:
        term = item['term']
        model = item.get('model', 'unknown')
        
        for ont_name, ont_res in item['ontologies'].items():
            # One Shot
            one_shot = ont_res.get('one_shot', {})
            if "error" in one_shot:
                rows.append({
                    "term": term,
                    "model": model,
                    "ontology": ont_name,
                    "strategy": "one_shot",
                    "classification": "ERROR",
                    "info": one_shot["error"],
                    "reasoning": ""
                })
            else:
                rows.append({
                    "term": term,
                    "model": model,
                    "ontology": ont_name,
                    "strategy": "one_shot",
                    "classification": one_shot.get("classification", "N/A"),
                    "info": f"Conf: {one_shot.get('confidence', 'N/A')}",
                    "reasoning": one_shot.get("reasoning", "").replace("\n", " ")
                })
                
            # Hierarchical
            hier = ont_res.get('hierarchical', {})
            if "error" in hier:
                rows.append({
                    "term": term,
                    "model": model,
                    "ontology": ont_name,
                    "strategy": "hierarchical",
                    "classification": "ERROR",
                    "info": hier["error"],
                    "reasoning": ""
                })
            else:
                path_str = " -> ".join(hier.get("path", []))
                rows.append({
                    "term": term,
                    "model": model,
                    "ontology": ont_name,
                    "strategy": "hierarchical",
                    "classification": hier.get("final_class", "N/A"),
                    "info": f"Path: {path_str}",
                    "reasoning": str(hier.get("trace", [])).replace("\n", " ")
                })

    with open(tsv_path, 'w', newline='') as f:
        fieldnames = ["term", "model", "ontology", "strategy", "classification", "info", "reasoning"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Converted results to {tsv_path}")

if __name__ == "__main__":
    main()