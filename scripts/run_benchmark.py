import os
import sys
import json
import subprocess
from tqdm import tqdm
import pandas as pd

# Add current directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from evaluate_taxonomy import load_data, evaluate_domain

# Configuration
DATASET_FILE = "datasets/benchmark_10_domains.json"
MODELS = {
    "Gemini 2.5 Flash": "google/gemini-2.5-flash",
    "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
    "GPT-4o": "openai/gpt-4o",
    "Llama 3.3 70B": "meta-llama/llama-3.3-70b-instruct",
    "Llama 3.2 3B": "meta-llama/llama-3.2-3b-instruct",
    "Mistral Large": "mistralai/mistral-large-2411",
    "Qwen 2.5 72B": "qwen/qwen-2.5-72b-instruct",
    "DeepSeek V3": "deepseek/deepseek-chat",
    # Small Models
    "Llama 3.1 8B": "meta-llama/llama-3.1-8b-instruct",
    "Gemini 2.0 Flash Lite": "google/gemini-2.0-flash-lite-001",
    "Gemini 2.5 Flash Lite": "google/gemini-2.5-flash-lite",
    "Qwen 2.5 7B": "qwen/qwen-2.5-7b-instruct",
    "Gemma 2 9B": "google/gemma-2-9b-it"
}

def run_experiment(model_name, model_id):
    output_file = f"experiment/taxonomy_benchmark_{model_name.replace(' ', '_').lower()}.json"
    
    if os.path.exists(output_file):
        print(f"--- Skipping generation for {model_name}: File already exists.")
        return output_file

    print(f"\n>>> Running Experiment for {model_name} ({model_id})")
    
    # Run generation script
    cmd = [
        "uv", "run", 
        "--with", "requests", "--with", "python-dotenv", "--with", "tqdm",
        "experiment/generate_taxonomy.py",
        DATASET_FILE,
        output_file,
        "--model", model_id
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running generation for {model_name}: {e}")
        return None
        
    return output_file

def evaluate_results(dataset_file, taxonomy_file):
    # Capture stdout to suppress detailed logs during benchmark
    from io import StringIO
    original_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        data, tax, _ = load_data(dataset_file, taxonomy_file)
        
        total_links = 0
        total_cycles = 0
        total_violations = 0
        total_warnings = 0
        
        domain_stats = {}
        
        for domain in data:
            if domain in tax:
                stats = evaluate_domain(domain, data[domain], tax[domain])
                
                total_links += stats['links_count']
                total_cycles += len(stats['cycles'])
                total_violations += len(stats['violations'])
                total_warnings += len(stats['warnings'])
                
                domain_stats[domain] = stats
                
        return {
            "total_links": total_links,
            "total_cycles": total_cycles,
            "total_violations": total_violations,
            "total_warnings": total_warnings,
            "domain_details": domain_stats
        }
        
    except Exception as e:
        sys.stdout = original_stdout
        print(f"Error evaluating {taxonomy_file}: {e}")
        return None
    finally:
        sys.stdout = original_stdout

def main():
    results = []
    
    for friendly_name, model_id in MODELS.items():
        taxonomy_file = run_experiment(friendly_name, model_id)
        
        if taxonomy_file and os.path.exists(taxonomy_file):
            print(f"Evaluating {friendly_name}...")
            stats = evaluate_results(DATASET_FILE, taxonomy_file)
            
            if stats:
                results.append({
                    "Model": friendly_name,
                    "Total Links": stats["total_links"],
                    "Violations (Critical)": stats["total_violations"],
                    "Cycles (Critical)": stats["total_cycles"],
                    "Warnings (Constitution)": stats["total_warnings"]
                })
        else:
            print(f"Skipping evaluation for {friendly_name} (Generation failed).")

    # Create DataFrame and Markdown Table
    df = pd.DataFrame(results)
    markdown_table = df.to_markdown(index=False)
    
    report_content = f"""# Benchmark Report: Ontology Taxonomy Generation

**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d')}
**Dataset:** 10 Domains (35 terms each) including "Treatment of bronchitis", "Cycling", etc.
**Evaluation Criteria:** OntoClean Constraints (Rigidity, Constitution, Cycle Detection).

## Summary Table

{markdown_table}

## Interpretation

*   **Total Links:** Higher is usually better (more connections found), provided they are correct.
*   **Violations (Critical):** Rigid Child is-a Anti-Rigid Parent. (e.g., Person is-a Student). MUST be 0.
*   **Cycles (Critical):** Circular dependencies. MUST be 0.
*   **Warnings:** Object is-a Material (e.g., Ring is-a Gold). Likely "Made-of" confusion. Should be low.

"""
    
    with open("experiment/BENCHMARK_REPORT.md", "w") as f:
        f.write(report_content)
        
    print("\nBenchmark Complete! Report saved to experiment/BENCHMARK_REPORT.md")
    print(markdown_table)

if __name__ == "__main__":
    main()
