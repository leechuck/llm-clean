import re
import csv
import sys
from pdfminer.high_level import extract_text

def parse_terms(text):
    # Normalize unicode spaces and hyphens
    text = text.replace('\u00a0', ' ')
    text = text.replace('‑', '-')
    
    # Normalize whitespace to single spaces
    normalized_text = re.sub(r'\s+', ' ', text)
    
    # Pattern: Number. Term as in "Description"
    # We use negative lookahead to ensure we don't cross into another question number.
    # We look for:
    # 1. A number and a dot (\d+\.)
    # 2. Whitespace
    # 3. The Term: A sequence of characters that does NOT contain a number followed by a dot.
    # 4. " as in "
    # 5. The Description in quotes.
    
    pattern = re.compile(r'(\d+)\.\s+((?:(?!\d+\.).)*?)\s+as in\s+"(.*?)"')
    
    matches = pattern.findall(normalized_text)
    
    terms = []
    seen_terms = set()
    
    for m in matches:
        num, term, desc = m
        
        try:
            if int(num) < 6:
                continue
        except ValueError:
            continue
            
        term = term.strip()
        desc = desc.strip()
        
        # Clean up term: sometimes it might capture "Comments" if the structure is weird, 
        # but the lookahead should prevent crossing "17. Comments 18."
        # However, "17. Comments" itself doesn't have "as in", so it shouldn't match.
        
        if term in seen_terms:
            continue
            
        terms.append((term, desc))
        seen_terms.add(term)
        
    return terms

def main():
    pdf_path = "resources/full_survey.pdf"
    output_path = "resources/survey_terms.tsv"
    
    print(f"Extracting text from {pdf_path}...")
    try:
        text = extract_text(pdf_path)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        sys.exit(1)
    
    print("Parsing terms...")
    terms = parse_terms(text)
    
    # Sort by number? Regex findall returns in order.
    # But let's sort by term number just in case.
    # Wait, the list is (term, desc), I lost the number in the list.
    # But matches has (num, term, desc).
    # Let's trust the document order.
    
    print(f"Found {len(terms)} terms.")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(["Term", "Description"])
        for term, desc in terms:
            writer.writerow([term, desc])
            
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()
