import argparse
import json
import os
import sys
import requests
from dotenv import load_dotenv
from tqdm import tqdm

def generate_domain_list(model, num_domains, api_key):
    """Generates a list of distinct domains."""
    prompt = f"""**Role:** You are a Senior Researcher in Formal Ontology.

**Objective:** Select {num_domains} distinct, complex domains to stress-test an OntoClean methodology classifier.
Examples: "Cybersecurity", "Maritime Law", "Molecular Biology", "Urban Planning", "MMORPG Gaming", "Treatment of bronchitis", "Cycling", "Beans".

**Output Format:**
Return a single JSON object:
{{
  "domains": ["List", "of", "strings"]
}}
"""
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/leechuck/llm-clean", 
        "X-Title": "Ontological Dataset Generator"
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return json.loads(content)['domains']
    except Exception as e:
        print(f"Error generating domains: {e}", file=sys.stderr)
        sys.exit(1)

def generate_domain_data(model, domain, num_terms, api_key):
    """Generates the gold standard dataset for a single domain."""
    prompt = f"""Role: You are an Expert Computational Ontologist specializing in the OntoClean methodology.

Objective: Generate a large, rigorous "Gold Standard" dataset to stress-test an ontology classification algorithm. 

Parameters:
    Domain: {domain}
    Count: Generate exactly {num_terms} terms.

**Crucial Generation Strategy:**
To ensure a complex resulting taxonomy, you must generate two types of terms mixed together:

1. **The Taxonomic Core (~40% of terms):**
   - You MUST include vertical chains of "Is-A" relationships.
   - Example: Entity -> Living Thing -> Animal -> Bird -> Raptor -> Eagle -> Golden Eagle.
   - Ensure you have at least 2 distinct deep branches (depth 3-4).

2. **The Ontological Traps (~60% of terms):**
   - For the terms above, generate related "Trap" terms that are *not* subtypes but are easily confused.
   - **Parts:** (e.g., "Wing", "Beak" for Bird).
   - **Materials:** (e.g., "Flesh", "Keratin").
   - **Roles:** (e.g., "Predator", "Pet", "Migrant").
   - **Phases:** (e.g., "Larva", "Fledgling").

**Property Definitions (Strict Adherence):**
    Rigidity (R): +R (Essential/Type), ~R (Non-rigid/Role/Phase).
    Identity (I): +I (Countable), -I (Mass/Stuff).
    Unity (U): +U (Whole), -U (Part/Amount).
    Dependence (D): +D (Needs other), -D (Independent).

**Output Format:** 
Provide ONLY a valid JSON object. The list should be flat (not nested).
{{
  "domain": "{domain}",
  "dataset": [
    {{
      "term": "Term Name",
      "properties": {{ "R": "...", "I": "...", "U": "...", "D": "..." }},
      "derived_class": "Type / Role / Phase / Material",
      "note": "Brief explanation"
    }}
  ]
}}
"""
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/leechuck/llm-clean", 
        "X-Title": "Ontological Dataset Generator"
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        print(f"Error generating data for domain '{domain}': {e}", file=sys.stderr)
        return None

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Generate ontological stress-test datasets via LLM.")
    parser.add_argument("output_file", help="Path to the output JSON file.")
    parser.add_argument("--model", default="google/gemini-2.0-flash-001", 
                        help="OpenRouter model ID (default: google/gemini-2.0-flash-001).")
    parser.add_argument("--num-domains", type=int, default=10, 
                        help="Number of domains to generate (default: 10).")
    parser.add_argument("--num-terms", type=int, default=15,
                        help="Number of terms per domain (default: 15).")
    parser.add_argument("--domains", nargs="+", help="Specific list of domains to generate data for.")
    
    args = parser.parse_args()
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
        
    if args.domains:
        domains = args.domains
        print(f"Using provided domains: {', '.join(domains)}")
    else:
        print(f"1. Generating list of {args.num_domains} domains using {args.model}...")
        domains = generate_domain_list(args.model, args.num_domains, api_key)
        print(f"Domains selected: {', '.join(domains)}")
    
    all_datasets = []
    
    print(f"2. Generating {args.num_terms} terms for each domain...")
    for domain in tqdm(domains):
        success = False
        for attempt in range(3):
            data = generate_domain_data(args.model, domain, args.num_terms, api_key)
            if data:
                all_datasets.append(data)
                success = True
                break
            else:
                print(f"  [Attempt {attempt+1}/3] Failed for '{domain}'. Retrying...", file=sys.stderr)
        
        if not success:
            print(f"  [Error] Failed to generate data for '{domain}' after 3 attempts.", file=sys.stderr)
            
    final_output = {"datasets": all_datasets}
    
    # Write to file
    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2)
            
    print(f"Successfully generated dataset and saved to {args.output_file}")

if __name__ == "__main__":
    main()
