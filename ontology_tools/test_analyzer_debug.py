#!/usr/bin/env python3
"""
Debug script to test analyzer with background file
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzer import OntologyAnalyzer

# Test with the same parameters that are failing
try:
    print("Initializing analyzer with anthropic model...")
    analyzer = OntologyAnalyzer(
        model="anthropic",
        background_file="resources/converted_text_files/guarino_text_files/01-guarino00formal-converted-corrected.txt"
    )
    print("Analyzer initialized successfully")

    print("\nAnalyzing 'Red' term...")
    result = analyzer.analyze("Red", description=None)

    print("\nAnalysis successful!")
    print(f"Result: {result}")

except FileNotFoundError as e:
    print(f"\nFile not found: {e}")
    print("Please run this from the repository root directory")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
