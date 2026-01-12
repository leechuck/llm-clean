import json
import os
import sys
import argparse
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ontology_tools.classifier import OntologyClassifier

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_all_classes(ontology_data):
    classes = set()
    classes.add(ontology_data['root'])
    for parent, children in ontology_data['classes'].items():
        classes.add(parent)
        for child in children:
            classes.add(child)
    return sorted(list(classes))

def run_hierarchical(classifier, term_data, ontology_name, ontology_data):
    current_class = ontology_data['root']
    path = [current_class]
    reasoning_trace = []
    
    descriptions = ontology_data.get('descriptions', {})
    examples = ontology_data.get('examples', {})

    while True:
        children = ontology_data['classes'].get(current_class, [])
        if not children:
            break
            
        try:
            result = classifier.classify_hierarchical_step(
                term_data['term'], 
                term_data['description'], 
                ontology_name, 
                current_class, 
                children,
                descriptions,
                examples
            )
            
            selected = result.get('selected_class')
            reasoning = result.get('reasoning')
            reasoning_trace.append(f"{current_class} -> {selected}: {reasoning}")
            
            if selected == current_class or selected not in children:
                # Stop if same class selected or invalid child
                break
            
            current_class = selected
            path.append(current_class)
            
        except Exception as e:
            print(f"Error in hierarchical step for {term_data['term']}: {e}", file=sys.stderr)
            break
            
    return {
        "final_class": current_class,
        "path": path,
        "trace": reasoning_trace
    }

def main():
    parser = argparse.ArgumentParser(description="Run Ontology Classification Experiment")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of terms to process (0 for all)")
    parser.add_argument("--model", default="openai/gpt-4o", help="Model ID")
    parser.add_argument("--output", help="Custom output JSON path")
    args = parser.parse_args()

    # Paths relative to this script location or project root? 
    # Current script is in experiments/stevens_repro/scripts/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    results_dir = os.path.join(base_dir, "results")
    
    terms = load_json(os.path.join(data_dir, "input_terms.json"))
    ontologies = load_json(os.path.join(data_dir, "ontologies.json"))
    
    if args.limit > 0:
        terms = terms[:args.limit]

    classifier = OntologyClassifier(model=args.model)
    
    results = []
    results_path = args.output if args.output else os.path.join(results_dir, "experiment_results.json")
    
    # Load existing to append/resume if needed
    if os.path.exists(results_path):
        try:
            results = load_json(results_path)
            print(f"Loaded {len(results)} existing results.")
        except:
            print("Could not load existing results, starting fresh.")
    
    processed_terms = {r['term'] for r in results}

    for term_entry in tqdm(terms, desc="Processing Terms"):
        term = term_entry['term']
        
        if term in processed_terms:
            continue
        
        term_results = {
            "term": term,
            "description": term_entry['description'],
            "model": args.model,
            "ontologies": {}
        }
        
        for ont_name, ont_data in ontologies.items():
            descriptions = ont_data.get('descriptions', {})
            examples = ont_data.get('examples', {})
            
            # One Shot
            try:
                all_cls = get_all_classes(ont_data)
                one_shot_res = classifier.classify_one_shot(
                    term, 
                    term_entry['description'], 
                    ont_name, 
                    all_cls,
                    descriptions,
                    examples
                )
            except Exception as e:
                print(f"One-shot error {term} {ont_name}: {e}")
                one_shot_res = {"error": str(e)}

            # Hierarchical
            try:
                hier_res = run_hierarchical(classifier, term_entry, ont_name, ont_data)
            except Exception as e:
                print(f"Hierarchical error {term} {ont_name}: {e}")
                hier_res = {"error": str(e)}
                
            term_results["ontologies"][ont_name] = {
                "one_shot": one_shot_res,
                "hierarchical": hier_res
            }
            
        results.append(term_results)
        
        # Save incrementally
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)

    print(f"Completed experiment. Results saved to {results_path}")

if __name__ == "__main__":
    main()