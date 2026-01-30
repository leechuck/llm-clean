import argparse
import sys
import os

# Ensure the project root is in sys.path so we can import ontology_tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology_tools.analyzer import OntologyAnalyzer

def main():
    parser = argparse.ArgumentParser(description="Assign Ontological Properties via LLM.")
    parser.add_argument("term", help="The entity term to analyze.")
    parser.add_argument("--desc", help="Additional description of the entity.")
    parser.add_argument("--usage", help="Example usage context.")
    parser.add_argument("--model",
                       default="google/gemini-3-flash-preview",
                       help="""
                                OpenRouter model ID. Supported: google/gemini-3-flash-preview (default), anthropic/claude-4.5-sonnet. \n
                                You can also use 'gemini' or 'anthropic' as shortcuts for the models.
                            """
                        )
    args = parser.parse_args()
    
    try:
        analyzer = OntologyAnalyzer(model=args.model)
        result = analyzer.analyze(args.term, args.desc, args.usage)
        
        props = result.get("properties", {})
        print(f"Analysis for '{args.term}':")
        print(f"  Rigidity:   {props.get('rigidity', 'N/A')}")
        print(f"  Identity:   {props.get('identity', 'N/A')}")
        print(f"  Unity:      {props.get('unity', 'N/A')}")
        print(f"  Dependence: {props.get('dependence', 'N/A')}")
        print(f"  Class:      {result.get('classification', 'N/A')}")
        print(f"  Reasoning:  {result.get('reasoning', 'N/A')}")
        
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()