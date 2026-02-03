import os
import sys
import pandas as pd
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from evaluate_taxonomy import load_data, evaluate_domain

DATASET_FILE = "datasets/benchmark_10_domains.json"
FILES = {
    "Llama 3.2 3B (Agentic)": "experiment/taxonomy_agentic_llama-3.2-3b-instruct.json",
    "Llama 3.1 8B (Agentic)": "experiment/taxonomy_agentic_llama-3.1-8b-instruct.json",
    # "Qwen 2.5 7B (Agentic)": "experiment/taxonomy_agentic_qwen-2.5-7b-instruct.json"
}

def evaluate_results(dataset_file, taxonomy_file):
    try:
        data, tax, _ = load_data(dataset_file, taxonomy_file)
        
        total_links = 0
        total_cycles = 0
        total_violations = 0
        total_warnings = 0
        
        for domain in data:
            if domain in tax:
                stats = evaluate_domain(domain, data[domain], tax[domain])
                total_links += stats['links_count']
                total_cycles += len(stats['cycles'])
                total_violations += len(stats['violations'])
                total_warnings += len(stats['warnings'])
                
        return {
            "total_links": total_links,
            "total_cycles": total_cycles,
            "total_violations": total_violations,
            "total_warnings": total_warnings
        }
    except Exception as e:
        print(f"Error evaluating {taxonomy_file}: {e}")
        return None

def main():
    results = []
    
    for friendly_name, file_path in FILES.items():
        if os.path.exists(file_path):
            print(f"Evaluating {friendly_name}...")
            stats = evaluate_results(DATASET_FILE, file_path)
            
            if stats:
                results.append({
                    "Model": friendly_name,
                    "Total Links": stats["total_links"],
                    "Violations (Critical)": stats["total_violations"],
                    "Cycles (Critical)": stats["total_cycles"],
                    "Warnings (Constitution)": stats["total_warnings"]
                })
        else:
            print(f"File not found: {file_path}")

    # Report
    if results:
        df = pd.DataFrame(results)
        print("\nAgentic Benchmark Results:")
        print(df.to_markdown(index=False))
        
        # Save to file
        with open("experiment/AGENTIC_BENCHMARK_REPORT.md", "w") as f:
            f.write("# Agentic Benchmark Results\n\n")
            f.write(df.to_markdown(index=False))
            f.write("\n\n*Note: Agentic workflow involves a Taxonomist Agent proposing links and a Critic Agent (OntoClean Expert) vetting them.*")

if __name__ == "__main__":
    main()
