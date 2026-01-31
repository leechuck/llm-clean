import os
import json
import requests
import re
import time
from dotenv import load_dotenv

class OntologyClassifier:
    # Supported models for ontology classification
    SUPPORTED_MODELS = [
        "gemini",
        "anthropic",
        "google/gemini-3-flash-preview",
        "anthropic/claude-4.5-sonnet",
        "openai/gpt-4o"
    ]

    def __init__(self, api_key=None, model="gemini", background_file=None):
        # Load environment variables from .env file
        load_dotenv()

        # Validate model
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model}. "
                f"Supported models are: {', '.join(self.SUPPORTED_MODELS)}"
            )

        # Set up default models for Anthropic and Gemini
        if model == "anthropic":
            model = "anthropic/claude-4.5-sonnet"
        elif model == "gemini":
            model = "google/gemini-3-flash-preview"
        else:
            model = model

        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.background_file = background_file
        self.background_content = None

        if not self.api_key:
            raise ValueError("api key environment variable not set or not provided.")

        # Load background information if provided
        if self.background_file:
            self._load_background_file()

    def _load_background_file(self):
        """Load background information from a file (supports .txt and .pdf)."""
        if not os.path.exists(self.background_file):
            raise FileNotFoundError(f"Background file not found: {self.background_file}")

        file_ext = os.path.splitext(self.background_file)[1].lower()

        if file_ext == '.txt':
            with open(self.background_file, 'r', encoding='utf-8') as f:
                self.background_content = f.read()
        elif file_ext == '.pdf':
            # Try to import PDF library
            try:
                import PyPDF2
                with open(self.background_file, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text_parts = []
                    for page in pdf_reader.pages:
                        text_parts.append(page.extract_text())
                    self.background_content = '\n'.join(text_parts)
            except ImportError:
                raise ImportError(
                    "PyPDF2 is required to read PDF files. "
                    "Install it with: pip install PyPDF2\n"
                    "Alternatively, convert your PDF to .txt format first."
                )
        else:
            raise ValueError(f"Unsupported file type: {file_ext}. Supported types: .txt, .pdf")

        # Warn if background content is very large (may cause context issues)
        MAX_CHARS = 50000  # ~12,500 tokens at 4 chars/token
        if len(self.background_content) > MAX_CHARS:
            import sys
            print(f"Warning: Background file is large ({len(self.background_content)} chars). "
                  f"Truncating to {MAX_CHARS} chars to avoid context issues.", file=sys.stderr)
            self.background_content = self.background_content[:MAX_CHARS]

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
                # Strip markdown code fences if present
                content = content.strip()
                content = re.sub(r'^```(?:json)?\s*\n?', '', content)
                content = re.sub(r'\n?```\s*$', '', content)
                content = content.strip()

                # Try to extract JSON if there's text before/after it
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)

                # Remove trailing commas
                content_cleaned = re.sub(r",\s*([\}\]])", r"\1", content)

                # Try to parse
                try:
                    return json.loads(content_cleaned)
                except json.JSONDecodeError as e:
                    # Try additional cleanup
                    content_cleaned = re.sub(r'//.*?\n', '\n', content_cleaned)
                    content_cleaned = re.sub(r'/\*.*?\*/', '', content_cleaned, flags=re.DOTALL)
                    content_cleaned = re.sub(r',(\s*[}\]])', r'\1', content_cleaned)
                    try:
                        return json.loads(content_cleaned)
                    except json.JSONDecodeError:
                        if attempt == retries - 1:
                            raise RuntimeError(
                                f"Error parsing JSON response from LLM.\n"
                                f"Parse error: {e}\n"
                                f"Raw output (first 1000 chars): {content[:1000]}\n"
                                f"Cleaned output (first 1000 chars): {content_cleaned[:1000]}"
                            )
                        # If not last attempt, continue to retry
                        continue

            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    error_msg = f"API Request failed: {e}"
                    if hasattr(e, 'response') and e.response is not None:
                        error_msg += f"\nStatus Code: {e.response.status_code}\nResponse: {e.response.text}"
                    raise RuntimeError(error_msg)
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

        # Build system prompt with optional background content
        if self.background_content:
            system_prompt = f"""You are an expert Ontologist specializing in the {ontology_name} upper ontology.

Use the following background information to guide your classification:

{self.background_content}

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
        else:
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

        # Build system prompt with optional background content
        if self.background_content:
            system_prompt = f"""You are an expert Ontologist specializing in the {ontology_name} upper ontology.

Use the following background information to guide your classification:

{self.background_content}

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
        else:
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