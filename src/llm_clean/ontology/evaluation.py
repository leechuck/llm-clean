import argparse
import json
import sys
from collections import defaultdict

def load_data(dataset_file, taxonomy_file):
    """Loads and merges dataset properties with taxonomy structure."""
    with open(dataset_file, 'r', encoding='utf-8') as f:
        data_json = json.load(f)
        
    with open(taxonomy_file, 'r', encoding='utf-8') as f:
        tax_json = json.load(f)
    
    model_name = tax_json.get("model", "Unknown Model")
        
    # Map domains for easy access
    domains_data = {d['domain']: d['dataset'] for d in data_json['datasets']}
    domains_tax = {d['domain']: d['taxonomy'] for d in tax_json['datasets']}
    
    return domains_data, domains_tax, model_name

def get_properties(term, domain_data):
    """Finds properties for a given term in the domain dataset."""
    for item in domain_data:
        if item['term'] == term:
            return item['properties']
    return None

def check_rigidity_constraint(child_term, child_props, parent_term, parent_props):
    """
    Rule: A Rigid (+R) class cannot be a subclass of an Anti-Rigid (~R) class.
    """
    c_rigid = child_props.get('R')
    p_rigid = parent_props.get('R')
    
    if c_rigid == '+R' and p_rigid == '~R':
        return f"VIOLATION: Rigid Child '{child_term}' (+R) cannot be a subclass of Anti-Rigid Parent '{parent_term}' (~R)."
    return None

def check_constitution_constraint(child_term, child_props, parent_term, parent_props):
    """
    Rule: An Object (+I/+U) should not be a subclass of a Material (-I/-U).
    This usually indicates a 'Made-Of' relationship mistaken for 'Is-A'.
    """
    c_identity = child_props.get('I')
    c_unity = child_props.get('U')
    
    p_identity = parent_props.get('I')
    p_unity = parent_props.get('U')
    
    is_child_object = (c_identity == '+I' or c_unity == '+U')
    is_parent_material = (p_identity == '-I' and p_unity == '-U')
    
    if is_child_object and is_parent_material:
        return f"WARNING (Constitution Trap): Object '{child_term}' (+I/+U) is classified as subclass of Material '{parent_term}' (-I/-U). Likely 'Made-Of' relation."
    return None

def evaluate_domain(domain_name, domain_data, taxonomy):
    print(f"\n--- Evaluating Domain: {domain_name} ---")
    
    violations = []
    warnings = []
    links_count = 0
    
    # 1. Build Adjacency List for Cycle Detection
    graph = defaultdict(list)
    
    for child, parents in taxonomy.items():
        # Handle cases where parents might be a single string instead of list (legacy format support)
        if isinstance(parents, str):
            parents = [parents]
        if parents is None:
            parents = []
            
        child_props = get_properties(child, domain_data)
        if not child_props:
            print(f"  [!] Term '{child}' found in taxonomy but not in dataset definition.")
            continue
            
        for parent in parents:
            if not parent: continue # Skip null/empty parents
            
            links_count += 1
            graph[child].append(parent)
            
            parent_props = get_properties(parent, domain_data)
            if not parent_props:
                print(f"  [!] Parent term '{parent}' not found in dataset definition.")
                continue
            
            # Check Constraints
            r_msg = check_rigidity_constraint(child, child_props, parent, parent_props)
            if r_msg: violations.append(r_msg)
            
            c_msg = check_constitution_constraint(child, child_props, parent, parent_props)
            if c_msg: warnings.append(c_msg)

    # 2. Cycle Detection
    visited = set()
    recursion_stack = set()
    cycles = []

    def dfs(node, path):
        visited.add(node)
        recursion_stack.add(node)
        path.append(node)
        
        if node in taxonomy:
            parents = taxonomy[node]
            if isinstance(parents, str): parents = [parents]
            if parents:
                for parent in parents:
                    if parent in recursion_stack:
                        cycle_segment = path[path.index(parent):] + [parent]
                        cycles.append(" -> ".join(cycle_segment))
                    elif parent not in visited:
                        dfs(parent, path)
        
        path.pop()
        recursion_stack.remove(node)

    for term in taxonomy:
        if term not in visited:
            dfs(term, [])

    # Report
    print(f"  Total Links Checked: {links_count}")
    
    if cycles:
        print(f"  [CRITICAL] Cycles Detected ({len(cycles)}):")
        for c in cycles:
            print(f"    - {c}")
    else:
        print("  Cycles: None")

    if violations:
        print(f"  [FAIL] Rigid Validation Violations ({len(violations)}):")
        for v in violations:
            print(f"    - {v}")
    else:
        print("  Rigid Validation: PASS")
        
    if warnings:
        print(f"  [WARN] Potential Constitution Traps ({len(warnings)}):")
        for w in warnings:
            print(f"    - {w}")
    else:
        print("  Constitution Checks: PASS")

    return {
        "violations": violations,
        "cycles": cycles,
        "warnings": warnings,
        "links_count": links_count
    }

def main():
    parser = argparse.ArgumentParser(description="Evaluate Taxonomy against OntoClean Constraints.")
    parser.add_argument("dataset_file", help="Path to the generated dataset JSON (Ground Truth).")
    parser.add_argument("taxonomy_file", help="Path to the taxonomy experiment JSON.")
    
    args = parser.parse_args()
    
    try:
        data, tax, model_name = load_data(args.dataset_file, args.taxonomy_file)
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        sys.exit(1)
        
    print(f"Evaluating Taxonomy generated by model: {model_name}")
    total_errors = 0
    
    for domain in data:
        if domain in tax:
            stats = evaluate_domain(domain, data[domain], tax[domain])
            total_errors += len(stats["violations"]) + len(stats["cycles"])
        else:
            print(f"\nSkipping domain '{domain}' (not found in taxonomy file).")

    if total_errors > 0:
        print(f"\nOverall: FAILED with {total_errors} critical errors.")
        sys.exit(1)
    else:
        print("\nOverall: SUCCESS (No critical violations found).")
        sys.exit(0)

if __name__ == "__main__":
    main()