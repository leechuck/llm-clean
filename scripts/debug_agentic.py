import os
import json
import re
import sys
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Reuse constants
ONTOCLEAN_CONTEXT = """...""" # I'll skip full text for brevity in this debug script, just generic
# Actually I need the real context to get approvals.
ONTOCLEAN_CONTEXT = """
You are an expert in Formal Ontology and the OntoClean methodology (Guarino & Welty).
Your job is to CRITIQUE proposed "IS-A" (subsumption) links in a taxonomy.
Definitions:
1. Rigidity (+R, -R): Rigid (+R) essential. Anti-Rigid (~R) contingent.
Constraint: ~R CANNOT subsume +R.
2. Identity (+I, -I): +I carries identity. -I does not.
Constraint: +I CANNOT subsume -I.
3. Unity (+U, ~U): +U is a whole. ~U is amount.
Constraint: ~U CANNOT subsume +U.
Task:
User will provide a proposed link: "Child IS-A Parent".
1. Infer meta-properties.
2. Check for violations.
3. If VIOLATION: Reply "REJECT: <Explanation>".
4. If VALID: Reply "APPROVE".
"""

TAXONOMIST_PROMPT = """
You are an expert Taxonomist.
Your goal is to organize a list of terms into a strict "IS-A" (subclass) hierarchy.
Rules:
1. Strict IS-A.
2. Input: List of terms.
3. Action: Pick ONE term and assign a PARENT from the list (or "Thing").
4. Correction: If rejected, fix it.
Format:
Return ONLY the JSON object:
{"child": "Term", "parent": "ParentTerm"}
"""

def create_chat_model(model_id: str):
    return ChatOpenAI(
        model=model_id,
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.0
    )

def main():
    model_id = "meta-llama/llama-3.2-3b-instruct"
    domain = "Treatment of bronchitis"
    terms = ["Medical Procedure", "Bronchitis Treatment", "Pharmacological Treatment", "Antibiotic Therapy"] # Small subset
    
    taxonomist_model = create_chat_model(model_id)
    critic_model = create_chat_model(model_id)
    
    taxonomy_output = {t: [] for t in terms}
    placed_terms = set()
    
    for term in sorted(terms):
        valid_link = False
        attempts = 0
        while not valid_link and attempts < 3:
            context = f"""
            Domain: {domain}
            Terms: {json.dumps(terms)}
            Current Term to Place: "{term}"
            Previously Placed: {json.dumps(list(placed_terms))}
            Existing Hierarchy: {json.dumps(taxonomy_output)}
            Task: Assign a parent for "{term}".
            """
            messages = [SystemMessage(content=TAXONOMIST_PROMPT), HumanMessage(content=context)]
            try:
                print(f"Asking Taxonomist for {term}...")
                response = taxonomist_model.invoke(messages)
                content = response.content
                match = re.search(r'{{.*}}', content, re.DOTALL)
                if match:
                    decision = json.loads(match.group(0))
                    parent = decision.get("parent")
                    if parent:
                        print(f"Taxonomist proposes: {term} -> {parent}")
                        # Critic
                        critic_prompt = f"Taxonomist proposes: '{term}' IS-A '{parent}'."
                        critic_res = critic_model.invoke([SystemMessage(content=ONTOCLEAN_CONTEXT), HumanMessage(content=critic_prompt)])
                        critique = critic_res.content
                        if "REJECT" in critique.upper():
                            print(f"REJECTED: {critique}")
                            attempts += 1
                        else:
                            print(f"APPROVED: {term} -> {parent}")
                            if parent != "Thing":
                                taxonomy_output[term] = [parent]
                            else:
                                taxonomy_output[term] = []
                            valid_link = True
                    else:
                        print("No parent in JSON")
                        attempts += 1
                else:
                    print(f"No JSON: {repr(content)}")
                    attempts += 1
            except Exception as e:
                print(f"Error: {e}")
                attempts += 1
        
        placed_terms.add(term)

    print("\nFinal Taxonomy:")
    print(json.dumps(taxonomy_output, indent=2))

if __name__ == "__main__":
    main()
