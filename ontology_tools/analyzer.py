import os
import json
import requests
import sys
from dotenv import load_dotenv

class OntologyAnalyzer:
    # Supported models for ontological analysis
    SUPPORTED_MODELS = [
        "gemini",
        "anthropic",
        "google/gemini-3-flash-preview",
        "anthropic/claude-sonnet-4-5-20250929"
    ]

    def __init__(self, api_key=None, model="gemini"):
        # Load environment variables from .env file
        load_dotenv()

        # Validate model
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model}. "
                f"Supported models are: {', '.join(self.SUPPORTED_MODELS)}"
            )
        # Set up defaul models for Anthropic and Gemini
        if model == "anthropic":
            model = "anthropic/claude-sonnet-4-5"
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        elif model == "gemini":
            model = "google/gemini-3-flash-preview"
            self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        else:
            model = model
            self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        if not self.api_key:
            raise ValueError("api key environment variable not set or not provided.")

    def analyze(self, term, description=None, usage=None):
        system_prompt = """You are an expert Ontological Analyst specializing in the "Formal Ontology of Properties" methodology by Guarino and Welty (2000). 
Your task is to analyze a given entity (term) and assign its 5 ontological meta-properties based on the paper's framework.

The 5 Meta-Properties:
1. **Rigidity (R)**: 
   - **+R (Rigid)**: Essential to all instances in all possible worlds.
   - **-R (Non-Rigid)**: Not essential to some instances.
   - **~R (Anti-Rigid)**: Essential *not* to be essential (e.g., Role, Phase).

2. **Identity (I) - Carries Identity**:
   - **+I**: The property carries an Identity Condition (IC).
   - **-I**: The property does not carry an IC.

3. **Own Identity (O) - Supplies Identity**:
   - **+O**: The property supplies its *own* global Identity Condition.
   - **-O**: The property does not supply its own IC (it might inherit it, or have none).
   *Constraint*: If **+O**, then **+I** must be true.

4. **Unity (U)**: 
   - **+U (Unifying)**: Instances are intrinsic wholes.
   - **-U (Non-Unifying)**: Instances are not necessarily wholes.
   - **~U (Anti-Unity)**: Instances are strictly sums/aggregates.

5. **Dependence (D)**: 
   - **+D (Dependent)**: Instances intrinsically depend on something else to exist.
   - **-D (Independent)**: Instances can exist alone.

Return your analysis in strict JSON format:
{
  "properties": {
    "rigidity": "+R" | "-R" | "~R",
    "identity": "+I" | "-I",
    "own_identity": "+O" | "-O",
    "unity": "+U" | "-U" | "~U",
    "dependence": "+D" | "-D"
  },
  "classification": "Sortal/Role/Mixin/etc",
  "reasoning": "Brief explanation."
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
            
            # Robust parsing: handle potential trailing commas or other minor LLM output quirks
            import re
            content_cleaned = re.sub(r",\s*([\]}])", r"\1", content)
            
            return json.loads(content_cleaned)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"API Request failed: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nStatus Code: {e.response.status_code}\nResponse: {e.response.text}"
            raise RuntimeError(error_msg)
        except json.JSONDecodeError:
            raise RuntimeError(f"Error parsing JSON response from LLM.\nRaw output: {content}")