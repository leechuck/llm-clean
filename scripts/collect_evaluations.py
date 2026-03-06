import argparse
import json
import pandas as pd
import sys
from pathlib import Path


def load_evaluation(file_path):
    """Load evaluation results from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('evaluation_summary', {}).get('metrics', {})
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def extract_row_data(summary):
    """Extract row data from evaluation summary."""
    row_data = {}

    # Add total evaluated
    # row_data['total_evaluated'] = summary.get('total_evaluated', 0)

    # Extract metrics for each property
    # metrics = summary.get('metrics', {})
    # properties = ['rigidity', 'identity', 'own_identity', 'unity', 'dependence']
    properties = summary.keys()  # dynamically get properties from summary

    for prop in properties:
        prop_data = summary.get(prop, {})
        row_data[f'{prop}_correct'] = prop_data.get('correct', 0)
        row_data[f'{prop}_total'] = prop_data.get('total', 0)
        row_data[f'{prop}_accuracy'] = prop_data.get('accuracy', 0.0)

    # Extract exact match
    # exact_match = summary.get('exact_match', {})
    # row_data['exact_match_correct'] = exact_match.get('correct', 0)
    # row_data['exact_match_total'] = exact_match.get('total', 0)
    # row_data['exact_match_accuracy'] = exact_match.get('accuracy', 0.0)

    return row_data


def infer_format_from_extension(file_path):
    """Infer output format from file extension."""
    ext = Path(file_path).suffix.lower()
    format_map = {
        '.csv': 'csv',
        '.tsv': 'tsv',
        '.md': 'md',
        '.json': 'json'
    }
    return format_map.get(ext)


def save_dataframe(df, output_path, output_format):
    """Save DataFrame in specified format."""
    if output_format == 'csv':
        df.to_csv(output_path)
        print(f"Results saved to {output_path} (CSV format)")
    elif output_format == 'tsv':
        df.to_csv(output_path, sep='\t', index=True)
        print(f"Results saved to {output_path} (TSV format)")
    elif output_format == 'md':
        try:
            df.to_markdown(output_path, index=True)
            print(f"Results saved to {output_path} (Markdown format)")
        except ImportError:
            print(
                "Error: Markdown output requires 'tabulate' package. "
                "Install with: pip install tabulate",
                file=sys.stderr
            )
            sys.exit(1)
    elif output_format == 'json':
        df.to_json(output_path, orient='index', indent=2, index=True)
        print(f"Results saved to {output_path} (JSON format)")
    else:
        print(f"Error: Unsupported format '{output_format}'", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Collect and aggregate evaluation results from multiple JSON files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect two evaluations and display
  python collect_evaluations.py --files eval1.json eval2.json --indexes model1 model2

  # Save as CSV (inferred from extension)
  python collect_evaluations.py --files eval1.json eval2.json --indexes model1 model2 --output results.csv

  # Save as TSV with explicit format
  python collect_evaluations.py --files eval1.json eval2.json --indexes model1 model2 --output results.txt --output-format tsv
        """
    )
    parser.add_argument(
        '--files',
        nargs='+',
        required=True,
        help="Paths to evaluation JSON files produced by evaluate_analysis.py"
    )
    parser.add_argument(
        '--indexes',
        nargs='+',
        required=True,
        help="Row index labels for each file (must match number of files)"
    )
    parser.add_argument(
        '--output',
        help="Path to save the aggregated results (optional)"
    )
    parser.add_argument(
        '--output-format',
        choices=['csv', 'tsv', 'md', 'json'],
        help="Output format (overrides extension-based inference). Choices: csv, tsv, md, json"
    )

    args = parser.parse_args()

    # Validate that files and indexes have the same length
    if len(args.files) != len(args.indexes):
        print(
            f"Error: Number of files ({len(args.files)}) must match "
            f"number of indexes ({len(args.indexes)})",
            file=sys.stderr
        )
        sys.exit(1)

    # Collect data from all files
    rows = []
    for file_path, index in zip(args.files, args.indexes):
        print(f"Loading {file_path} with index '{index}'...")
        summary = load_evaluation(file_path)
        summary['index'] = index  # add index to summary for DataFrame
        rows.append(summary)

    # Create DataFrame
    df = pd.DataFrame(rows)
    df.set_index('index', inplace=True)

    # set index name for better output formatting
    df.index.name = 'background_file'

    # Display DataFrame
    print("\nAggregated Results:")
    print("=" * 80)
    print(df.to_string())
    print("=" * 80)

    # Save if output is specified
    if args.output:
        # Determine format
        output_format = args.output_format
        if output_format is None:
            output_format = infer_format_from_extension(args.output)
            if output_format is None:
                print(
                    f"Error: Could not infer format from extension '{Path(args.output).suffix}'. "
                    f"Please specify --output-format",
                    file=sys.stderr
                )
                sys.exit(1)

        save_dataframe(df, args.output, output_format)


if __name__ == "__main__":
    main()
