import os
import json
import requests
import re
import time

class OntologyClassifier:
    def __init__(self, api_key=None, model="openai/gpt-4o"):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set or not provided.")

    def _call_llm(self, system_prompt, user_content):
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
            "X-Title": "Ontological Classification Tool"
        }

        retries = 3
        for attempt in range(retries):
            try:
                response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
                if response.status_code == 429:
                    time.sleep(2 ** attempt) # Exponential backoff
                    continue
                response.raise_for_status()
                result = response.json()
                
                content = result['choices'][0]['message']['content']
                
                # Robust parsing
                content_cleaned = re.sub(r",\s*([\}\]])", r"\1", content)
                return json.loads(content_cleaned)
                    
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    error_msg = f"API Request failed: {e}"
                    if hasattr(e, 'response') and e.response is not None:
                        error_msg += f"\nStatus Code: {e.response.status_code}\nResponse: {e.response.text}"
                    raise RuntimeError(error_msg)
            except json.JSONDecodeError:
                if attempt == retries - 1:
                    raise RuntimeError(f"Error parsing JSON response from LLM.\nRaw output: {content}")
        return None

    def _format_class_info(self, classes, descriptions, examples):
        """Helper to format class info block"""
        lines = []
        for cls in classes:
            desc = descriptions.get(cls, "No definition provided.") if descriptions else "No definition provided."
            ex = examples.get(cls, []) if examples else []
            ex_str = f" (e.g. {', '.join(ex)})" if ex else ""
            lines.append(f"- **{cls}**: {desc}{ex_str}")
        return "\n".join(lines)

    def classify_one_shot(self, term, description, ontology_name, all_classes, descriptions=None, examples=None):
        class_info = self._format_class_info(all_classes, descriptions, examples)
        
        system_prompt = f"""You are an expert Ontologist specializing in the {ontology_name} upper ontology.
Your task is to classify a given domain entity into exactly one of the provided {ontology_name} classes.
Choose the most specific and ontologically correct class.

Available Classes and Definitions:
{class_info}

Return your answer in JSON format:
{{
  "classification": "ClassName",
  "confidence": "High/Medium/Low",
  "reasoning": "Brief explanation referencing the definition."
}}
"""
        user_content = f"Classify the following entity:\nTerm: {term}\nDescription: {description}"
        return self._call_llm(system_prompt, user_content)

    def classify_hierarchical_step(self, term, description, ontology_name, current_class, children, descriptions=None, examples=None):
        class_info = self._format_class_info(children, descriptions, examples)

        system_prompt = f"""You are an expert Ontologist specializing in the {ontology_name} upper ontology.
We are traversing the ontology hierarchically. The entity '{term}' has been identified as a type of '{current_class}'.
Now, choose the best sub-class for '{term}' from the following candidates.

Candidates:
{class_info}

If the entity clearly belongs to the parent '{current_class}' but does not fit well into any of the specific children (i.e. it is a leaf at this level or ambiguous), you can choose '{current_class}' itself.

Return your answer in JSON format:
{{
  "selected_class": "ClassName",
  "reasoning": "Brief explanation referencing the definition."
}}
"""
        user_content = f"Entity: {term}\nDescription: {description}"
        return self._call_llm(system_prompt, user_content)