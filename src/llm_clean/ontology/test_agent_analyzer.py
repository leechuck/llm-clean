#!/usr/bin/env python3
"""
Test script demonstrating the AgentOntologyAnalyzer with different background files.
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_analyzer import AgentOntologyAnalyzer


def test_without_background():
    """Test analysis without any background files (uses default prompts)."""
    print("=" * 60)
    print("Test 1: Analysis WITHOUT background files")
    print("=" * 60)

    try:
        analyzer = AgentOntologyAnalyzer(model="gemini", use_default_backgrounds=False)
        result = analyzer.analyze("Student", description="A person enrolled in a university")

        print(f"\nAnalysis of 'Student':")
        print(json.dumps(result, indent=2))
        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_with_default_property_backgrounds():
    """Test analysis with property-specific default background files."""
    print("=" * 60)
    print("Test 2: Analysis WITH property-specific DEFAULT backgrounds")
    print("=" * 60)

    try:
        # This will use the DEFAULT_BACKGROUND_FILES by default
        analyzer = AgentOntologyAnalyzer(model="gemini")
        result = analyzer.analyze("Student", description="A person enrolled in a university")

        print(f"\nAnalysis of 'Student' with property-specific defaults:")
        print(json.dumps(result, indent=2))
        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_with_single_default_background():
    """Test analysis with a single background file for all properties."""
    print("=" * 60)
    print("Test 3: Analysis WITH single default background file")
    print("=" * 60)

    # This assumes you have a background file at this path
    background_file = "resources/converted_text_files/guarino_text_files/01-guarino00formal-converted-corrected.txt"

    if not os.path.exists(background_file):
        print(f"Skipping: Background file not found at {background_file}")
        print("Please adjust the path or create the file.")
        return

    try:
        analyzer = AgentOntologyAnalyzer(
            model="gemini",
            default_background_file=background_file
        )
        result = analyzer.analyze("Student", description="A person enrolled in a university")

        print(f"\nAnalysis of 'Student' with single background:")
        print(json.dumps(result, indent=2))
        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_with_custom_property_backgrounds():
    """Test analysis with different background files for different properties."""
    print("=" * 60)
    print("Test 4: Analysis WITH custom property-specific background files")
    print("=" * 60)

    # Example: Different background files for different properties
    background_files = {
        "rigidity": "resources/rigidity_guide.txt",
        "identity": "resources/identity_guide.txt",
        "unity": "resources/unity_guide.txt",
        # dependence and own_identity will use default if provided
    }

    # Check which files exist
    existing_files = {}
    for prop, filepath in background_files.items():
        if os.path.exists(filepath):
            existing_files[prop] = filepath
            print(f"Found background for {prop}: {filepath}")
        else:
            print(f"Note: {filepath} not found, skipping property-specific background for {prop}")

    if not existing_files:
        print("\nSkipping: No property-specific background files found.")
        print("Create files like resources/rigidity_guide.txt to test this feature.")
        return

    try:
        analyzer = AgentOntologyAnalyzer(
            model="gemini",
            background_files=existing_files
        )
        result = analyzer.analyze("Employee", description="A person working for an organization")

        print(f"\nAnalysis of 'Employee' with property-specific backgrounds:")
        print(json.dumps(result, indent=2))
        print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def test_comparison():
    """Compare results with and without background files."""
    print("=" * 60)
    print("Test 5: COMPARISON - Same term with/without background")
    print("=" * 60)

    term = "Red"
    desc = "The color red, as a property of objects"

    # Without background
    print(f"\nAnalyzing '{term}' WITHOUT background...")
    try:
        analyzer_no_bg = AgentOntologyAnalyzer(model="gemini", use_default_backgrounds=False)
        result_no_bg = analyzer_no_bg.analyze(term, description=desc)
        print("Properties (no background):", result_no_bg['properties'])
        print("Classification:", result_no_bg['classification'])
    except Exception as e:
        print(f"Error without background: {e}")
        result_no_bg = None

    # With background (if available)
    background_file = "resources/converted_text_files/guarino_text_files/01-guarino00formal-converted-corrected.txt"
    if os.path.exists(background_file):
        print(f"\nAnalyzing '{term}' WITH background...")
        try:
            analyzer_with_bg = AgentOntologyAnalyzer(
                model="gemini",
                default_background_file=background_file
            )
            result_with_bg = analyzer_with_bg.analyze(term, description=desc)
            print("Properties (with background):", result_with_bg['properties'])
            print("Classification:", result_with_bg['classification'])
        except Exception as e:
            print(f"Error with background: {e}")
            result_with_bg = None

        # Show differences
        if result_no_bg and result_with_bg:
            print("\n" + "=" * 40)
            print("DIFFERENCES:")
            print("=" * 40)
            for prop in ['rigidity', 'identity', 'own_identity', 'unity', 'dependence']:
                val_no_bg = result_no_bg['properties'].get(prop)
                val_with_bg = result_with_bg['properties'].get(prop)
                if val_no_bg != val_with_bg:
                    print(f"{prop:15} | No BG: {val_no_bg:3} | With BG: {val_with_bg:3} | DIFFERENT")
                else:
                    print(f"{prop:15} | Both: {val_no_bg:3} | SAME")
    else:
        print(f"\nSkipping comparison: Background file not found")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AgentOntologyAnalyzer Test Suite")
    print("=" * 60)
    print()

    # Run tests
    test_without_background()
    print("\n" * 2)

    test_with_default_property_backgrounds()
    print("\n" * 2)

    test_with_single_default_background()
    print("\n" * 2)

    test_with_custom_property_backgrounds()
    print("\n" * 2)

    test_comparison()
    print("\n" * 2)

    print("=" * 60)
    print("Tests complete!")
    print("=" * 60)
