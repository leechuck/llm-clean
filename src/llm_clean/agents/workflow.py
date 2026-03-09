import json
import re
from typing import List, Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from llm_clean.utils.llm import get_chat_model

ONTOCLEAN_CONTEXT = """
You are an expert in Formal Ontology and the OntoClean methodology (Guarino & Welty).
Your job is to CRITIQUE proposed "IS-A" (subsumption) links in a taxonomy.

**Definitions:**
1.  **Rigidity (+R, -R, ~R):**
    *   **+R (Rigid):** Essential property. Holds in all possible worlds. (e.g., PERSON, ANIMAL).
    *   **~R (Anti-Rigid):** Contingent property. Instances can cease to be this without ceasing to exist. (e.g., STUDENT, EMPLOYEE, AGENT).
    *   **Constraint:** ~R (Anti-Rigid) CANNOT subsume +R (Rigid).
2.  **Identity (+I, -I):**
    *   **+I (Sortal):** Carries identity criteria (Countable nouns like Apple, Planet).
    *   **-I (Non-Sortal):** No identity criteria (Adjectives like Red, or Mass nouns like Water).
    *   **Constraint:** +I CANNOT subsume -I.
3.  **Unity (+U, ~U):**
    *   **+U (Whole):** Holds together (e.g., Ocean, Ball).
    *   **~U (Anti-Unity):** Mere amount (e.g., Amount of Water).
    *   **Constraint:** ~U CANNOT subsume +U.

**Task:**
User will provide a proposed link: "Child IS-A Parent".
1.  Infer the meta-properties (+R, ~R, etc.) for Child and Parent.
2.  Check for violations.
3.  If VIOLATION: Reply "REJECT: <Explanation>".
4.  If VALID: Reply "APPROVE".
"""

TAXONOMIST_PROMPT = """
You are an expert Taxonomist.
Your goal is to organize a list of terms into a strict "IS-A" (subclass) hierarchy.

**Rules:**
1.  **Strict IS-A:** Only use true subclass relationships.
2.  **Format:** Return ONLY the JSON object for the single new link:
    {"child": "Term", "parent": "ParentTerm"}
"""

class OntoCleanWorkflow:
    """
    Implements an agentic workflow for taxonomy generation using OntoClean principles.
    Uses a 'Taxonomist' agent to propose links and a 'Critic' agent to validate them.
    """
    
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.taxonomist_model = get_chat_model(model_id)
        self.critic_model = get_chat_model(model_id)

    def _propose_link(self, term: str, domain: str, terms: List[str], 
                     placed_terms: set, existing_tax: Dict, 
                     last_critique: str = "") -> Optional[Dict]:
        """Ask the taxonomist to propose a parent for a term."""
        context = f"""
        Domain: {domain}
        Terms: {json.dumps(terms)}
        Current Term to Place: "{term}"
        Previously Placed: {json.dumps(list(placed_terms))}
        Existing Hierarchy: {json.dumps(existing_tax)}
        
        Task: Assign a parent for "{term}" from the list or "Thing".
        """
        if last_critique:
            context += f"""

Previous attempt REJECTED by Critic:
{last_critique}

Propose a different parent."""

        messages = [SystemMessage(content=TAXONOMIST_PROMPT), HumanMessage(content=context)]
        response = self.taxonomist_model.invoke(messages)
        
        match = re.search(r'\{.*?\}', response.content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                # Try cleaning trailing commas before closing brace
                cleaned = re.sub(r',\s*}', '}', match.group(0))
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    return None
        return None

    def _critique_link(self, term: str, parent: str, domain: str) -> str:
        """Ask the critic to approve or reject a link."""
        prompt = f'Taxonomist proposes: "{term}" IS-A "{parent}". Domain: {domain}'
        messages = [SystemMessage(content=ONTOCLEAN_CONTEXT), HumanMessage(content=prompt)]
        response = self.critic_model.invoke(messages)
        return response.content

    def process_domain(self, domain: str, terms: List[str]) -> Dict[str, List[str]]:
        """Generates a taxonomy for a single domain."""
        taxonomy = {t: [] for t in terms}
        placed_terms = set()
        
        for term in sorted(terms):
            valid_link = False
            attempts = 0
            last_critique = ""
            
            while not valid_link and attempts < 3:
                decision = self._propose_link(term, domain, terms, placed_terms, taxonomy, last_critique)
                if not decision:
                    attempts += 1
                    continue
                
                parent = decision.get("parent")
                if not parent:
                    attempts += 1
                    continue
                
                critique = self._critique_link(term, parent, domain)
                if "REJECT" in critique.upper():
                    last_critique = critique
                    attempts += 1
                else:
                    if parent != "Thing":
                        taxonomy[term] = [parent]
                    valid_link = True
            
            placed_terms.add(term)
        
        return taxonomy
