#!/usr/bin/env python3
"""
Analyze a single entity using specialized agents for each meta-property.
"""
import argparse
import sys
import os
import json

# Ensure the project root is in sys.path so we can import ontology_tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology_tools.agent_analyzer import AgentOntologyAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="Analyze entity using specialized agents for each ontological meta-property"
    )
    parser.add_argument("term", help="The entity term to analyze.")
    parser.add_argument("--desc", help="Additional description of the entity.")
    parser.add_argument("--usage", help="Example usage context.")
    parser.add_argument("--model",
                       default="google/gemini-3-flash-preview",
                       help="OpenRouter model ID. Supported: google/gemini-3-flash-preview (default), "
                            "anthropic/claude-4.5-sonnet. You can also use 'gemini' or 'anthropic' as shortcuts.")

    # Background file options
    parser.add_argument("--default-background", dest="default_background",
                       help="Default background file for all properties (.txt or .pdf). "
                            "Overrides property-specific defaults if provided.")
    parser.add_argument("--no-default-backgrounds", dest="no_default_backgrounds",
                       action="store_true",
                       help="Disable default property-specific background files")
    parser.add_argument("--rigidity-background", dest="rigidity_background",
                       help="Background file specifically for Rigidity analysis")
    parser.add_argument("--identity-background", dest="identity_background",
                       help="Background file specifically for Identity analysis")
    parser.add_argument("--own-identity-background", dest="own_identity_background",
                       help="Background file specifically for Own Identity analysis")
    parser.add_argument("--unity-background", dest="unity_background",
                       help="Background file specifically for Unity analysis")
    parser.add_argument("--dependence-background", dest="dependence_background",
                       help="Background file specifically for Dependence analysis")

    parser.add_argument("--output", "-o", help="Output file (JSON). If not specified, prints to stdout")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed reasoning for each property")

    args = parser.parse_args()

    try:
        # Build background_files dict
        background_files = {}
        if args.rigidity_background:
            background_files['rigidity'] = args.rigidity_background
        if args.identity_background:
            background_files['identity'] = args.identity_background
        if args.own_identity_background:
            background_files['own_identity'] = args.own_identity_background
        if args.unity_background:
            background_files['unity'] = args.unity_background
        if args.dependence_background:
            background_files['dependence'] = args.dependence_background

        # Initialize agent analyzer
        analyzer = AgentOntologyAnalyzer(
            model=args.model,
            background_files=background_files if background_files else None,
            default_background_file=args.default_background,
            use_default_backgrounds=not args.no_default_backgrounds
        )

        # Analyze the entity
        result = analyzer.analyze(args.term, args.desc, args.usage)

        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Results written to {args.output}")
        else:
            if args.verbose:
                # Detailed output
                print(json.dumps(result, indent=2))
            else:
                # Compact output
                props = result.get("properties", {})
                print(f"Analysis for '{args.term}':")
                print(f"  Rigidity:     {props.get('rigidity', 'N/A')}")
                print(f"  Identity:     {props.get('identity', 'N/A')}")
                print(f"  Own Identity: {props.get('own_identity', 'N/A')}")
                print(f"  Unity:        {props.get('unity', 'N/A')}")
                print(f"  Dependence:   {props.get('dependence', 'N/A')}")
                print(f"  Classification: {result.get('classification', 'N/A')}")

    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
