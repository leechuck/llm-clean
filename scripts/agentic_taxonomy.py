import os
import json
import argparse
import sys
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Configure OpenRouter environment
if "OPENROUTER_API_KEY" in os.environ:
    os.environ["OPENAI_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
    os.environ["OPENAI_API_BASE_URL"] = "https://openrouter.ai/api/v1"

ONTOCLEAN_CONTEXT = """
You are an expert in Formal Ontology and the OntoClean methodology (Guarino & Welty).
Your job is to CRITIQUE proposed "IS-A" (subsumption) links in a taxonomy.

**Definitions:**
1.  **Rigidity (+R, -R, ~R):**
    *   **+R (Rigid):** Essential property. Holds in all possible worlds. (e.g., PERSON, ANIMAL).
    *   **~R (Anti-Rigid):** Contingent property. Instances can cease to be this without ceasing to exist. (e.g., STUDENT, EMPLOYEE, AGENT).
    *   **Constraint:** ~R (Anti-Rigid) CANNOT subsume +R (Rigid).
        *   *INVALID:* Person (+R) IS-A Student (~R). (Because a person isn't essentially a student).
        *   *INVALID:* Person (+R) IS-A Agent (~R). (If Agent is a role).
        *   *VALID:* Student (~R) IS-A Person (+R).

2.  **Identity (+I, -I):**
    *   **+I (Sortal):** Carries identity criteria (Countable nouns like Apple, Planet).
    *   **-I (Non-Sortal):** No identity criteria (Adjectives like Red, or Mass nouns like Water).
    *   **Constraint:** +I CANNOT subsume -I.
        *   *INVALID:* Red (-I) IS-A Apple (+I).

3.  **Unity (+U, ~U):**
    *   **+U (Whole):** Holds together (e.g., Ocean, Ball).
    *   **~U (Anti-Unity):** Mere amount (e.g., Amount of Water).
    *   **Constraint:** ~U CANNOT subsume +U.
        *   *INVALID:* Vase (+U) IS-A Clay (~U). (Vase is CONSTITUTED-BY Clay, not IS-A Clay).

**Task:**
User will provide a proposed link: "Child IS-A Parent".
1.  Infer the meta-properties (+R, ~R, etc.) for Child and Parent.
2.  Check for violations (especially Rigidity violations: Rigid Child IS-A Anti-Rigid Parent).
3.  If VIOLATION: Reply "REJECT: <Explanation>".
4.  If VALID: Reply "APPROVE".
"""

TAXONOMIST_PROMPT = """
You are an expert Taxonomist.
Your goal is to organize a list of terms into a strict "IS-A" (subclass) hierarchy.
You will build this step-by-step.

**Rules:**
1.  **Strict IS-A:** Only use true subclass relationships.
    *   Sparrow IS-A Bird (YES)
    *   Wheel IS-A Car (NO - Part-of)
    *   Baker IS-A Bread (NO)
2.  **Input:** I will give you a list of terms.
3.  **Action:** In each turn, pick ONE term from the list that hasn't been placed yet, and assign it a PARENT from the list (or "Thing" if it's a root).
4.  **Correction:** If the Critic rejects your link, propose a different parent or correct the relationship.

**Format:**
Return ONLY the JSON object for the single new link:
{"child": "Term", "parent": "ParentTerm"}
"""

def create_chat_model(model_id: str):
    # LangChain ChatOpenAI setup for OpenRouter
    return ChatOpenAI(
        model=model_id,
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.0
    )

def run_agentic_taxonomy(input_file, output_file, model_id):
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    datasets = data.get("datasets", [])
    results = []
    
    # Initialize Models
    taxonomist_model = create_chat_model(model_id)
    critic_model = create_chat_model(model_id)

    for dataset in datasets:
        domain = dataset.get("domain")
        terms = dataset.get("terms", [])
        if not terms and "dataset" in dataset:
            terms = [x["term"] for x in dataset["dataset"]]
            
        print(f"Processing domain: {domain} ({len(terms)} terms)")
        
        taxonomy_output = {t: [] for t in terms}
        placed_terms = set()
        sorted_terms = sorted(terms) 
        
        # Maintain history manually for the Taxonomist to keep context
        # Initial system message
        taxonomist_history = [SystemMessage(content=TAXONOMIST_PROMPT)]
        
        for term in sorted_terms:
            valid_link = False
            attempts = 0
            last_critique = ""
            
            while not valid_link and attempts < 3:
                # 1. Taxonomist proposes
                context = f"""
                Domain: {domain}
                Terms: {json.dumps(terms)}
                Current Term to Place: "{term}"
                Previously Placed: {json.dumps(list(placed_terms))}
                Existing Hierarchy: {json.dumps(taxonomy_output)}
                
                Task: Assign a parent for "{term}". 
                If it is a root concept in this list, use "Thing".
                Possible parents: {json.dumps(terms)} or "Thing".
                """
                
                if attempts > 0:
                    context += f"\n\nPrevious attempt REJECTED by Critic:\n{last_critique}\n\nINSTRUCTION: You MUST either (a) propose a different, valid parent, or (b) if you are certain, strictly justify why the previous choice was correct constraints. Output the JSON decision again."
                
                messages = [SystemMessage(content=TAXONOMIST_PROMPT), HumanMessage(content=context)]
                
                try:
                    response = taxonomist_model.invoke(messages)
                    content = response.content
                    
                    # Parse JSON
                    match = re.search(r'\{.*?\}', content, re.DOTALL)
                    if match:
                        decision = json.loads(match.group(0))
                        parent = decision.get("parent")
                        if parent:
                            # 2. Critic Checks
                            critic_prompt = f"""
                            Taxonomist proposes: "{term}" IS-A "{parent}".
                            Domain: {domain}
                            
                            Evaluate this link based on OntoClean (Rigidity, etc.).
                            If "{parent}" is "Thing", usually APPROVE unless "{term}" is not a noun.
                            """
                            critic_messages = [SystemMessage(content=ONTOCLEAN_CONTEXT), HumanMessage(content=critic_prompt)]
                            critic_res = critic_model.invoke(critic_messages)
                            critique = critic_res.content
                            
                            print(f"  Proposed: {term} -> {parent}")
                            
                            if "REJECT" in critique.upper():
                                print(f"  -> REJECTED: {critique[:100]}...")
                                last_critique = critique
                                attempts += 1
                            else:
                                print(f"  -> APPROVED: {term} -> {parent}")
                                if parent != "Thing":
                                    if parent in taxonomy_output:
                                        taxonomy_output[term] = [parent]
                                    else:
                                         taxonomy_output[term] = [parent]
                                else:
                                    taxonomy_output[term] = []
                                valid_link = True
                        else:
                             print(f"  Debug: No 'parent' key in JSON. Content: {content[:100]}...")
                             attempts += 3 
                    else:
                        print(f"  Debug: No JSON found in response. Content: {content[:100]}...")
                        attempts += 3 
                except Exception as e:
                    print(f"  Error parsing/critiquing: {e}")
                    attempts += 3
            
            if not valid_link:
                # Fallback: Root
                taxonomy_output[term] = []
            
            placed_terms.add(term)
            
        dataset["taxonomy"] = taxonomy_output
        results.append(dataset)

        # Save progress incrementally
        final_output = {"model": model_id + "-agentic", "datasets": results}
        with open(output_file, 'w') as f:
            json.dump(final_output, f, indent=2)

    # Final save (redundant but safe)
    with open(output_file, 'w') as f:
        json.dump(final_output, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("--model", required=True)
    args = parser.parse_args()
    
    run_agentic_taxonomy(args.input_file, args.output_file, args.model)