import argparse
import json
import os
import sys
import requests
from dotenv import load_dotenv
from tqdm import tqdm

def generate_taxonomy(model, domain, terms, api_key):
    """Generates a taxonomy for a given list of terms using an LLM."""
    
    # improved output format description to support multiple parents and strict validation
    prompt = f"""Role: You are an Expert Taxonomist.

Objective: specific terms from a domain are provided. Identify strict "Is-A" (Subclass) relationships between them *if and only if* they exist.

**Input List:** {json.dumps(terms)}

**Constraints & Rules:**
1.  **Strict "Is-A" ONLY:**
    *   Target: "Sparrow" -> Parent: "Bird" (YES, a Sparrow IS A Bird).
    *   Target: "Wheel" -> Parent: "Car" (NO, Wheel is PART OF Car).
    *   Target: "Baker" -> Parent: "Bread" (NO, Baker MAKES Bread).
    *   Target: "Gold" -> Parent: "Ring" (NO, Ring is MADE OF Gold).
2.  **Closed World:** You can ONLY use terms from the Input List as parents.
3.  **Disconnectivity is Good:** These terms were generated to be diverse. It is highly likely that many terms have NO parent in this specific list. **Do not force a connection.**
    *   If "Dog" and "Computer" are the only terms, neither is the parent of the other. Return `[]` for both.
4.  **Multiple Parents:** Allowed only if valid (e.g., "Mother" might be child of "Female" and "Parent").

**Task:**
For every term in the input list, return a list of its direct parents from the list.

**Output Format:**
JSON object. Keys are the terms, values are lists of parents strings.
{{
  "taxonomy": {{
    "Term A": ["Parent B"],
    "Term B": [],
    "Term C": []
  }}
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
        "X-Title": "Taxonomy Generator"
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        
        # Robust JSON extraction
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
            
        return json.loads(content)
    except Exception as e:
        # print(f"Error generating taxonomy for domain '{domain}': {e}", file=sys.stderr)
        return None

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Generate taxonomies from term lists via LLM.")
    parser.add_argument("input_file", help="Path to the input JSON file (containing domains and terms).")
    parser.add_argument("output_file", help="Path to the output JSON file.")
    parser.add_argument("--model", default="google/gemini-2.0-flash-001", 
                        help="OpenRouter model ID (default: google/gemini-2.0-flash-001).")
    
    args = parser.parse_args()
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
        
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(args.input_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    datasets = input_data.get("datasets", [])
    if not datasets:
        print("Error: No 'datasets' key found in input file.", file=sys.stderr)
        sys.exit(1)

    results = []
    
    print(f"Generating taxonomies for {len(datasets)} domains using {args.model}...")
    
    for dataset in tqdm(datasets):
        domain = dataset.get("domain")
        
        # Extract terms list. 
        # The input format has "terms" as a list of strings (simple format) 
        # OR "dataset" list of objects with "term" key (gold standard format).
        # We need to handle both.
        
        terms = []
        if "terms" in dataset:
            terms = dataset["terms"]
        elif "dataset" in dataset:
            terms = [item["term"] for item in dataset["dataset"]]
            
        if not terms:
            print(f"Warning: No terms found for domain '{domain}'. Skipping.")
            continue
            
        taxonomy_data = generate_taxonomy(args.model, domain, terms, api_key)
        
        if taxonomy_data:
            # Merge the result with the original domain info
            dataset_result = dataset.copy()
            dataset_result["taxonomy"] = taxonomy_data.get("taxonomy", {})
            results.append(dataset_result)
            
    final_output = {"model": args.model, "datasets": results}
    
    # Write to file
    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2)
            
    print(f"Successfully generated taxonomies and saved to {args.output_file}")

if __name__ == "__main__":
    main()