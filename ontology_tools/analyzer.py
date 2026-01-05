import os
import json
import requests
import sys

class OntologyAnalyzer:
    def __init__(self, api_key=None, model="openai/gpt-4o"):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set or not provided.")

    def analyze(self, term, description=None, usage=None):
        system_prompt = """You are an expert Ontological Analyst specializing in the "Formal Ontology of Properties" methodology by Guarino and Welty (2000). 
Your task is to analyze a given entity (term) and assign its ontological meta-properties based on the paper's framework.

The meta-properties are:
1. **Rigidity (R)**: 
   - **+R (Rigid)**: The property is essential to all its instances in all possible worlds (e.g., Person).
   - **-R (Non-Rigid)**: The property is not essential to some instances.
   - **~R (Anti-Rigid)**: The property is essential *not* to be essential; instances can cease to be this property without ceasing to exist (e.g., Student).

2. **Identity (I)**:
   - **+O (Own Identity)**: The property supplies its own Identity Condition (IC) (e.g., Person).
   - **+I (Carries Identity)**: The property carries an IC inherited from a subsuming property (e.g., Student carries IC from Person).
   - **-I (No Identity)**: The property does not carry an IC (e.g., Red).

3. **Unity (U)**: 
   - **+U (Unifying)**: Instances are intrinsic wholes (e.g., Ocean).
   - **-U (Non-Unifying)**: Instances are not necessarily wholes.
   - **~U (Anti-Unity)**: Instances are strictly sums/aggregates (e.g., Amount of Water).

4. **Dependence (D)**: 
   - **+D (Dependent)**: Instances intrinsically depend on something else to exist (e.g., Parent depends on Child).
   - **-D (Independent)**: Instances can exist alone (e.g., Person).

Return your analysis in strict JSON format with the following structure:
{
  "properties": {
    "rigidity": "+R" | "-R" | "~R",
    "identity": "+O" | "+I" | "-I",
    "unity": "+U" | "-U" | "~U",
    "dependence": "+D" | "-D"
  },
  "classification": "Sortal/Role/Mixin/etc",
  "reasoning": "Brief explanation of why these values were chosen."
}
"""

        user_content = f"Analyze the following entity:\n\nTerm: {term}\n"
        if description:
            user_content += f"Description: {description}\n"
        if usage:
            user_content += f"Usage context: {usage}\n"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"}
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/leechuck/llm-clean", 
            "X-Title": "Ontological Analysis Tool"
        }

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            
            content = result['choices'][0]['message']['content']
            return json.loads(content)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"API Request failed: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nStatus Code: {e.response.status_code}\nResponse: {e.response.text}"
            raise RuntimeError(error_msg)
        except json.JSONDecodeError:
            raise RuntimeError(f"Error parsing JSON response from LLM.\nRaw output: {content}")
