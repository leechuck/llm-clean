import os
import json
import requests
import sys
from dotenv import load_dotenv


class AgentOntologyAnalyzer:
    """
    Ontology analyzer that uses separate specialized agents for each meta-property.
    Each agent can optionally use a different background file for specialized guidance.
    """

    # Supported models for ontological analysis
    SUPPORTED_MODELS = [
        "gemini",
        "anthropic",
        "google/gemini-3-flash-preview",
        "anthropic/claude-4.5-sonnet"
    ]

    # Property names
    PROPERTIES = ["rigidity", "identity", "own_identity", "unity", "dependence"]

    # Default background files for each property
    DEFAULT_BACKGROUND_FILES = {
        "rigidity": "resources/converted_text_files/guarino_text_files/01-guarino00formal-rigidity.txt",
        "identity": "resources/converted_text_files/guarino_text_files/01-guarino00formal-identity.txt",
        "own_identity": "resources/converted_text_files/guarino_text_files/01-guarino00formal-identity.txt",
        "unity": "resources/converted_text_files/guarino_text_files/01-guarino00formal-unity.txt",
        "dependence": "resources/converted_text_files/guarino_text_files/01-guarino00formal-dependence.txt"
    }

    def __init__(self, api_key=None, model="gemini", background_files=None, default_background_file=None, use_default_backgrounds=True):
        """
        Initialize the agent-based analyzer.

        Args:
            api_key: OpenRouter API key (optional, will use env variable if not provided)
            model: Model to use (default: "gemini")
            background_files: Dict mapping property names to background file paths.
                             If provided, overrides default backgrounds for specified properties.
            default_background_file: Default background file to use for all properties.
                                    Overrides use_default_backgrounds if provided.
            use_default_backgrounds: If True (default), uses property-specific backgrounds from
                                    DEFAULT_BACKGROUND_FILES. Set to False to use no backgrounds.
        """
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

        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        if not self.api_key:
            raise ValueError("api key environment variable not set or not provided.")

        # Initialize background content for each property
        self.background_content = {}
        self.default_background_content = None

        # Load default background file if provided (overrides use_default_backgrounds)
        if default_background_file:
            self.default_background_content = self._load_background_file(default_background_file)
        # Otherwise, load property-specific default backgrounds if requested
        elif use_default_backgrounds:
            print("Loading default property-specific background files...", file=sys.stderr)
            for prop, file_path in self.DEFAULT_BACKGROUND_FILES.items():
                if os.path.exists(file_path):
                    try:
                        self.background_content[prop] = self._load_background_file(file_path)
                        print(f"  ✓ Loaded {prop}: {file_path}", file=sys.stderr)
                    except Exception as e:
                        print(f"  ✗ Failed to load {prop} background: {e}", file=sys.stderr)
                else:
                    print(f"  ⚠ Default background for {prop} not found: {file_path}", file=sys.stderr)

        # Load user-specified property-specific background files (overrides defaults)
        if background_files:
            for prop, file_path in background_files.items():
                if prop in self.PROPERTIES:
                    self.background_content[prop] = self._load_background_file(file_path)
                    print(f"  ✓ Loaded custom {prop} background: {file_path}", file=sys.stderr)
                else:
                    print(f"Warning: Unknown property '{prop}' in background_files. Ignoring.",
                          file=sys.stderr)

    def _load_background_file(self, file_path):
        """Load background information from a file (supports .txt and .pdf)."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Background file not found: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif file_ext == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text_parts = []
                    for page in pdf_reader.pages:
                        text_parts.append(page.extract_text())
                    content = '\n'.join(text_parts)
            except ImportError:
                raise ImportError(
                    "PyPDF2 is required to read PDF files. "
                    "Install it with: pip install PyPDF2"
                )
        else:
            raise ValueError(f"Unsupported file type: {file_ext}. Supported types: .txt, .pdf")

        # Warn if content is very large
        MAX_CHARS = 50000
        if len(content) > MAX_CHARS:
            print(f"Warning: Background file {file_path} is large ({len(content)} chars). "
                  f"Truncating to {MAX_CHARS} chars to avoid context issues.", file=sys.stderr)
            content = content[:MAX_CHARS]

        return content

    def _get_background_for_property(self, property_name):
        """Get background content for a specific property."""
        return self.background_content.get(property_name, self.default_background_content)

    def _call_llm(self, system_prompt, user_content):
        """Make API call to LLM."""
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
            "X-Title": "Ontological Analysis Tool - Agent Mode"
        }

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()

            content = result['choices'][0]['message']['content']

            # Robust JSON parsing
            import re

            content = content.strip()
            content = re.sub(r'^```(?:json)?\s*\n?', '', content)
            content = re.sub(r'\n?```\s*$', '', content)
            content = content.strip()

            # Extract JSON if there's text before/after it
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

            # Remove trailing commas
            content_cleaned = re.sub(r",\s*([\]}])", r"\1", content)

            try:
                return json.loads(content_cleaned)
            except json.JSONDecodeError as e:
                # Additional cleanup attempts
                content_cleaned = re.sub(r'//.*?\n', '\n', content_cleaned)
                content_cleaned = re.sub(r'/\*.*?\*/', '', content_cleaned, flags=re.DOTALL)
                content_cleaned = re.sub(r',(\s*[}\]])', r'\1', content_cleaned)

                try:
                    return json.loads(content_cleaned)
                except json.JSONDecodeError:
                    raise RuntimeError(
                        f"Error parsing JSON response from LLM.\n"
                        f"Parse error: {e}\n"
                        f"Raw output (first 1000 chars): {content[:1000]}\n"
                        f"Cleaned output (first 1000 chars): {content_cleaned[:1000]}"
                    )

        except requests.exceptions.RequestException as e:
            error_msg = f"API Request failed: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nStatus Code: {e.response.status_code}\nResponse: {e.response.text}"
            raise RuntimeError(error_msg)
        except KeyError as e:
            raise RuntimeError(f"Unexpected API response format: {e}\nResponse: {result}")

    def _analyze_rigidity(self, term, description=None, usage=None):
        """Specialized agent for analyzing Rigidity meta-property."""
        background = self._get_background_for_property("rigidity")

        if background:
            system_prompt = f"""You are an expert Ontological Analyst specializing in the Rigidity meta-property.

Use the following background information:

{background}

Your task is to analyze ONLY the Rigidity property of the given entity."""
        else:
            system_prompt = """You are an expert Ontological Analyst specializing in the Rigidity meta-property from Guarino and Welty (2000)."""

        system_prompt += """

**Rigidity (R)** - Analyze whether the property is essential to all its instances:
   - **+R (Rigid)**: Essential to ALL instances in ALL possible worlds.
     Examples: Person (anything that is a person is necessarily a person), Physical Object
   - **-R (Non-Rigid)**: Not essential to some instances; instances can gain/lose it.
     Examples: Student (a person can become/stop being a student), Red Thing
   - **~R (Anti-Rigid)**: Essential NOT to be essential (contingent by definition).
     Examples: Role (like Student, Employee), Phase (like Child, Adult)

Return your analysis in strict JSON format:
{
  "value": "+R" | "-R" | "~R",
  "reasoning": "Brief explanation of why this entity has this rigidity value."
}
"""

        user_content = f"Analyze the Rigidity property of:\n\nTerm: {term}\n"
        if description:
            user_content += f"Description: {description}\n"
        if usage:
            user_content += f"Usage context: {usage}\n"

        return self._call_llm(system_prompt, user_content)

    def _analyze_identity(self, term, description=None, usage=None):
        """Specialized agent for analyzing Identity meta-property."""
        background = self._get_background_for_property("identity")

        if background:
            system_prompt = f"""You are an expert Ontological Analyst specializing in the Identity meta-property.

Use the following background information:

{background}

Your task is to analyze ONLY the Identity (Carries Identity) property of the given entity."""
        else:
            system_prompt = """You are an expert Ontological Analyst specializing in the Identity meta-property from Guarino and Welty (2000)."""

        system_prompt += """

**Identity (I) - Carries Identity Condition** - Does this property carry an identity condition for its instances?
   - **+I**: The property carries an Identity Condition (IC). Instances can be distinguished and re-identified.
     Examples: Person (has IC like DNA, fingerprints), Physical Object (has spatio-temporal continuity)
   - **-I**: The property does NOT carry an identity condition. No principled way to distinguish instances.
     Examples: Red (what makes one instance of red the same over time?), Amount of Matter

Return your analysis in strict JSON format:
{
  "value": "+I" | "-I",
  "reasoning": "Brief explanation of whether this entity carries an identity condition."
}
"""

        user_content = f"Analyze the Identity property of:\n\nTerm: {term}\n"
        if description:
            user_content += f"Description: {description}\n"
        if usage:
            user_content += f"Usage context: {usage}\n"

        return self._call_llm(system_prompt, user_content)

    def _analyze_own_identity(self, term, description=None, usage=None, identity_value=None):
        """Specialized agent for analyzing Own Identity meta-property."""
        background = self._get_background_for_property("own_identity")

        if background:
            system_prompt = f"""You are an expert Ontological Analyst specializing in the Own Identity meta-property.

Use the following background information:

{background}

Your task is to analyze ONLY the Own Identity (Supplies Identity) property of the given entity."""
        else:
            system_prompt = """You are an expert Ontological Analyst specializing in the Own Identity meta-property from Guarino and Welty (2000)."""

        system_prompt += """

**Own Identity (O) - Supplies Identity Condition** - Does this property supply its OWN identity condition?
   - **+O**: Supplies its own global identity condition.
     Examples: Person (supplies own IC), Physical Object (supplies own IC)
   - **-O**: Does not supply own IC (inherits it from a more general property, or has none).
     Examples: Student (inherits IC from Person), Red (has no IC to supply)

**IMPORTANT CONSTRAINT**: If +O, then +I must be true. You cannot supply an IC without carrying one.

"""

        if identity_value:
            system_prompt += f"Note: The Identity analysis determined this entity is {identity_value}.\n"

        system_prompt += """
Return your analysis in strict JSON format:
{
  "value": "+O" | "-O",
  "reasoning": "Brief explanation of whether this entity supplies its own identity condition."
}
"""

        user_content = f"Analyze the Own Identity property of:\n\nTerm: {term}\n"
        if description:
            user_content += f"Description: {description}\n"
        if usage:
            user_content += f"Usage context: {usage}\n"

        return self._call_llm(system_prompt, user_content)

    def _analyze_unity(self, term, description=None, usage=None):
        """Specialized agent for analyzing Unity meta-property."""
        background = self._get_background_for_property("unity")

        if background:
            system_prompt = f"""You are an expert Ontological Analyst specializing in the Unity meta-property.

Use the following background information:

{background}

Your task is to analyze ONLY the Unity property of the given entity."""
        else:
            system_prompt = """You are an expert Ontological Analyst specializing in the Unity meta-property from Guarino and Welty (2000)."""

        system_prompt += """

**Unity (U)** - Are instances of this property wholes with integrated parts?
   - **+U (Unifying)**: Instances are intrinsic wholes with clear mereological structure.
     Examples: Person (integrated biological system), Car (functional whole)
   - **-U (Non-Unifying)**: Instances are not necessarily wholes; parts may be arbitrary.
     Examples: Red Thing (scattered red objects), Amount of Water
   - **~U (Anti-Unity)**: Instances are strictly aggregates/sums without integration.
     Examples: Collection, Group, Scattered Object

Return your analysis in strict JSON format:
{
  "value": "+U" | "-U" | "~U",
  "reasoning": "Brief explanation of the unity characteristics of this entity."
}
"""

        user_content = f"Analyze the Unity property of:\n\nTerm: {term}\n"
        if description:
            user_content += f"Description: {description}\n"
        if usage:
            user_content += f"Usage context: {usage}\n"

        return self._call_llm(system_prompt, user_content)

    def _analyze_dependence(self, term, description=None, usage=None):
        """Specialized agent for analyzing Dependence meta-property."""
        background = self._get_background_for_property("dependence")

        if background:
            system_prompt = f"""You are an expert Ontological Analyst specializing in the Dependence meta-property.

Use the following background information:

{background}

Your task is to analyze ONLY the Dependence property of the given entity."""
        else:
            system_prompt = """You are an expert Ontological Analyst specializing in the Dependence meta-property from Guarino and Welty (2000)."""

        system_prompt += """

**Dependence (D)** - Do instances intrinsically depend on other entities?
   - **+D (Dependent)**: Instances necessarily depend on other entities to exist.
     Examples: Student (depends on School/Educational Institution), Parasite (depends on Host)
   - **-D (Independent)**: Instances can exist without depending on specific other entities.
     Examples: Person (independent), Physical Object (independent)

Return your analysis in strict JSON format:
{
  "value": "+D" | "-D",
  "reasoning": "Brief explanation of the dependence characteristics of this entity."
}
"""

        user_content = f"Analyze the Dependence property of:\n\nTerm: {term}\n"
        if description:
            user_content += f"Description: {description}\n"
        if usage:
            user_content += f"Usage context: {usage}\n"

        return self._call_llm(system_prompt, user_content)

    def _classify_entity(self, properties):
        """
        Determine entity classification based on meta-properties.
        Based on Guarino & Welty's OntoClean taxonomy.
        """
        r = properties.get('rigidity')
        i = properties.get('identity')
        o = properties.get('own_identity')
        u = properties.get('unity')
        d = properties.get('dependence')

        # Basic classifications based on rigidity and identity
        if r == '+R' and i == '+I' and o == '+O':
            return "Sortal (Rigid, supplies identity)"
        elif r == '+R' and i == '+I':
            return "Sortal (Rigid, carries identity)"
        elif r == '~R' and d == '+D':
            return "Role (Anti-rigid, dependent)"
        elif r == '~R':
            return "Role or Phase (Anti-rigid)"
        elif r == '-R' and i == '-I':
            return "Attribution (Non-rigid, no identity)"
        elif r == '-R':
            return "Category or Mixin (Non-rigid)"
        elif i == '-I':
            return "Attribution or Quality"
        else:
            return "Complex Type (see properties for details)"

    def analyze(self, term, description=None, usage=None):
        """
        Analyze entity using specialized agents for each meta-property.

        Returns:
            dict with structure:
            {
                "properties": {
                    "rigidity": "+R" | "-R" | "~R",
                    "identity": "+I" | "-I",
                    "own_identity": "+O" | "-O",
                    "unity": "+U" | "-U" | "~U",
                    "dependence": "+D" | "-D"
                },
                "reasoning": {
                    "rigidity": "...",
                    "identity": "...",
                    "own_identity": "...",
                    "unity": "...",
                    "dependence": "..."
                },
                "classification": "Sortal/Role/etc"
            }
        """
        properties = {}
        reasoning = {}

        # Analyze each property with its specialized agent
        print(f"Analyzing {term} with specialized agents...", file=sys.stderr)

        # 1. Rigidity
        print("  - Rigidity agent...", file=sys.stderr)
        rigidity_result = self._analyze_rigidity(term, description, usage)
        properties['rigidity'] = rigidity_result['value']
        reasoning['rigidity'] = rigidity_result['reasoning']

        # 2. Identity
        print("  - Identity agent...", file=sys.stderr)
        identity_result = self._analyze_identity(term, description, usage)
        properties['identity'] = identity_result['value']
        reasoning['identity'] = identity_result['reasoning']

        # 3. Own Identity (pass identity result for constraint checking)
        print("  - Own Identity agent...", file=sys.stderr)
        own_identity_result = self._analyze_own_identity(
            term, description, usage,
            identity_value=properties['identity']
        )
        properties['own_identity'] = own_identity_result['value']
        reasoning['own_identity'] = own_identity_result['reasoning']

        # 4. Unity
        print("  - Unity agent...", file=sys.stderr)
        unity_result = self._analyze_unity(term, description, usage)
        properties['unity'] = unity_result['value']
        reasoning['unity'] = unity_result['reasoning']

        # 5. Dependence
        print("  - Dependence agent...", file=sys.stderr)
        dependence_result = self._analyze_dependence(term, description, usage)
        properties['dependence'] = dependence_result['value']
        reasoning['dependence'] = dependence_result['reasoning']

        # Classify based on properties
        classification = self._classify_entity(properties)

        return {
            "properties": properties,
            "reasoning": reasoning,
            "classification": classification
        }
