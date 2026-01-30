import argparse
import sys
import os
import json
import subprocess

def test_groovy_owl_parsing(owl_path):
    """Test if Groovy can successfully parse an OWL file."""

    # Get path to extract_entities.groovy script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    groovy_script = os.path.join(script_dir, "extract_entities.groovy")

    # Check if groovy is installed
    try:
        version_result = subprocess.run(
            ["groovy", "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ Groovy found: {version_result.stdout.strip()}")
    except FileNotFoundError:
        print("✗ Groovy not found. Please install Groovy first.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"✗ Error checking Groovy version: {e}")
        return False

    # Check if OWL file exists
    if not os.path.exists(owl_path):
        print(f"✗ OWL file not found: {owl_path}")
        return False

    print(f"✓ OWL file found: {owl_path}")

    # Try to run the Groovy script
    print("\nAttempting to parse OWL file with Groovy/OWLAPI...")
    cmd = ["groovy", groovy_script, owl_path]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)

        # Try to parse JSON output
        try:
            entities = json.loads(result.stdout)
            print(f"✓ SUCCESS: Groovy successfully parsed the OWL file")
            print(f"✓ Found {len(entities)} entities")

            # Show first few entities as sample
            if entities:
                print("\nSample entities:")
                for entity in entities[:5]:
                    term = entity.get('term', 'N/A')
                    uri = entity.get('uri', 'N/A')
                    desc = entity.get('description', '')
                    desc_preview = desc[:50] + '...' if desc and len(desc) > 50 else desc
                    print(f"  - {term} ({uri})")
                    if desc_preview:
                        print(f"    Description: {desc_preview}")

            return True

        except json.JSONDecodeError as e:
            print(f"✗ FAILURE: Groovy executed but output is not valid JSON")
            print(f"JSON Error: {e}")
            print(f"\nGroovy output (first 500 chars):\n{result.stdout[:500]}")
            return False

    except subprocess.TimeoutExpired:
        print("✗ FAILURE: Groovy script timed out (120 seconds)")
        return False

    except subprocess.CalledProcessError as e:
        print(f"✗ FAILURE: Groovy script execution failed")
        print(f"\nError output:")
        print(e.stderr)

        # Check for common issues
        if "Error grabbing Grapes" in e.stderr:
            print("\n⚠ DIAGNOSIS: Grape dependency resolution failed")
            print("This usually means:")
            print("  1. Network connectivity issues with Maven Central")
            print("  2. Corrupted Grape cache (~/.groovy/grapes/)")
            print("  3. Firewall blocking Maven repository access")
            print("\nPossible solutions:")
            print("  - Check your internet connection")
            print("  - Try: rm -rf ~/.groovy/grapes/ (clears Grape cache)")
            print("  - Wait and retry (Maven Central may be temporarily unavailable)")
            print("\nNote: batch_analyze_owl_hybrid.py will automatically fall back to rdflib")

        return False

    except Exception as e:
        print(f"✗ FAILURE: Unexpected error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Test if Groovy can successfully parse an OWL ontology file"
    )
    parser.add_argument(
        "--input",
        default="ontology/guarino_messy.owl",
        help="Path to the OWL file to test (default: ontology/guarino_messy.owl)"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Groovy OWL Parsing Test")
    print("=" * 70)
    print()

    success = test_groovy_owl_parsing(args.input)

    print()
    print("=" * 70)
    if success:
        print("RESULT: ✓ Groovy OWL parsing is working correctly")
        sys.exit(0)
    else:
        print("RESULT: ✗ Groovy OWL parsing failed")
        print("\nThe hybrid script will use rdflib fallback instead.")
        sys.exit(1)

if __name__ == "__main__":
    main()
