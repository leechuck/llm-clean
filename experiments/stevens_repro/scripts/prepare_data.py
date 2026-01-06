import csv
import json
import os

def main():
    tsv_path = "entities_stevens.tsv"
    output_path = "experiments/stevens_repro/data/input_terms.json"
    
    # Known descriptions from the paper text
    descriptions = {
        "drinking a beer": "drinking a beer as in 'I like drinking a beer with my pizza.'",
        "air space": "air space as in 'We flew the airspace of three countries before we arrived.'",
        "clubbing": "We went clubbing every night, because I like many people dancing together.",
        "vacation location": "Parts of the world that you would vacation to, such as Paris or a particular resort.",
        "bus driver": "bus driver as in a person driving a bus (ambiguous between role and person).",
        "moment": "The moment I stepped out of the door of the plane, the air smelt good.",
        "timetable": "A set of facts... it is not about actual facts, because the timetable is also a timetable if the bus company is on strike."
    }

    terms = []
    if os.path.exists(tsv_path):
        with open(tsv_path, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            # If the TSV has no header and just terms, we might need to handle that
            # Checking file content first
            pass

    # Re-reading raw to be sure
    with open(tsv_path, 'r') as f:
        lines = f.readlines()
    
    # Assume first line is header 'term'
    header = lines[0].strip()
    data_lines = [l.strip() for l in lines[1:] if l.strip()]

    result = []
    for term in data_lines:
        desc = descriptions.get(term, f"{term} in the context of travel and tourism.")
        result.append({
            "term": term,
            "description": desc,
            "example": ""
        })

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Prepared {len(result)} items in {output_path}")

if __name__ == "__main__":
    main()
