#!/usr/bin/env python3
"""
Split data files into training and test sets.

This script takes a TSV, CSV, or JSON file as input and randomly splits it into
training and test sets based on specified proportions.

For TSV/CSV files: Randomly selects rows (preserving header)
For JSON files: Randomly selects top-level objects/items

Usage:
    python generate_train_test.py input.tsv --output-train train.tsv --output-test test.tsv
    python generate_train_test.py input.csv --output-train train.csv --output-test test.csv
    python generate_train_test.py input.json --output-train train.json --output-test test.json

    # Custom split ratios
    python generate_train_test.py input.tsv --train-size 0.8 --test-size 0.2 --output-train train.tsv --output-test test.tsv
"""

import argparse
import json
import csv
import sys
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.model_selection import train_test_split


def read_tsv_csv(file_path, delimiter="\t"):
    """
    Read TSV or CSV file and return header and rows.

    Args:
        file_path: Path to the file
        delimiter: Delimiter character (default: tab)

    Returns:
        tuple: (header, rows) where header is a list and rows is a list of lists
    """
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimiter)
        header = next(reader)  # First row is header
        rows = list(reader)
    return header, rows


def write_tsv_csv(file_path, header, rows, delimiter="\t"):
    """
    Write data to TSV or CSV file.

    Args:
        file_path: Path to the output file
        header: Header row (list)
        rows: Data rows (list of lists)
        delimiter: Delimiter character (default: tab)
    """
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerow(header)
        writer.writerows(rows)


def read_json(file_path):
    """
    Read JSON file and return data.

    Args:
        file_path: Path to the JSON file

    Returns:
        list or dict: The JSON data
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def write_json(file_path, data):
    """
    Write data to JSON file.

    Args:
        file_path: Path to the output file
        data: Data to write (typically a list or dict)
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def split_data(data, train_size=0.7, random_state=42):
    """
    Randomly split data into training and test sets using sklearn.

    Args:
        data: List of items to split
        train_size: Proportion for training set (default: 0.7)
        random_state: Random seed for reproducibility (default: 42)

    Returns:
        tuple: (train_data, test_data)
    """
    # Use sklearn's train_test_split for consistent splitting
    # Only pass train_size, sklearn will automatically calculate test_size
    train_data, test_data = train_test_split(
        data, train_size=train_size, random_state=random_state
    )

    return train_data, test_data


def detect_format(file_path):
    """
    Detect file format from extension.

    Args:
        file_path: Path to the file

    Returns:
        str: 'tsv', 'csv', or 'json'
    """
    ext = Path(file_path).suffix.lower()
    if ext == ".tsv":
        return "tsv"
    elif ext == ".csv":
        return "csv"
    elif ext == ".json":
        return "json"
    else:
        raise ValueError(
            f"Unsupported file format: {ext}. Supported: .tsv, .csv, .json"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Split data files into training and test sets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Split TSV file with default 70/30 ratio
  python generate_train_test.py data.tsv --output-train train.tsv --output-test test.tsv
  
  # Split CSV file with custom 80/20 ratio
  python generate_train_test.py data.csv --train-size 0.8 --test-size 0.2 --output-train train.csv --output-test test.csv
  
  # Split JSON file
  python generate_train_test.py data.json --output-train train.json --output-test test.json
  
  # Convert format during split (e.g., TSV to CSV)
  python generate_train_test.py data.tsv --output-train train.csv --output-test test.csv
        """,
    )

    parser.add_argument("input_file", help="Input file (TSV, CSV, or JSON)")

    parser.add_argument(
        "--output-train", required=True, help="Output file for training set"
    )

    parser.add_argument("--output-test", required=True, help="Output file for test set")

    parser.add_argument(
        "--train-size",
        type=float,
        default=0.7,
        help="Proportion of data for training set (default: 0.7)",
    )

    parser.add_argument(
        "--test-size",
        type=float,
        default=0.3,
        help="Proportion of data for test set (default: 0.3)",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )

    args = parser.parse_args()

    # Validate that train_size + test_size = 1.0 (approximately)
    total_size = args.train_size + args.test_size
    if abs(total_size - 1.0) > 0.01:
        print(
            f"Warning: train_size ({args.train_size}) + test_size ({args.test_size}) = {total_size} != 1.0",
            file=sys.stderr,
        )
        print(f"Adjusting test_size to {1.0 - args.train_size}", file=sys.stderr)
        args.test_size = 1.0 - args.train_size

    # Display seed being used
    print(f"Using random seed: {args.seed}")

    # Detect input format
    input_format = detect_format(args.input_file)
    output_train_format = detect_format(args.output_train)
    output_test_format = detect_format(args.output_test)

    print(f"Input format: {input_format.upper()}")
    print(f"Output format (train): {output_train_format.upper()}")
    print(f"Output format (test): {output_test_format.upper()}")

    # Read input file
    print(f"\nReading {args.input_file}...")

    if input_format in ["tsv", "csv"]:
        delimiter = "\t" if input_format == "tsv" else ","
        header, rows = read_tsv_csv(args.input_file, delimiter=delimiter)
        print(f"  Loaded {len(rows)} rows (+ 1 header row)")

        # Split the data
        train_rows, test_rows = split_data(
            rows, train_size=args.train_size, random_state=args.seed
        )

        print(f"\nSplit: {len(train_rows)} training, {len(test_rows)} test")
        print(f"  Training: {len(train_rows) / len(rows) * 100:.1f}%")
        print(f"  Test: {len(test_rows) / len(rows) * 100:.1f}%")

        # Write training set
        print(f"\nWriting training set to {args.output_train}...")
        if output_train_format == "json":
            # Convert to JSON format (list of dicts)
            train_data = [dict(zip(header, row)) for row in train_rows]
            write_json(args.output_train, train_data)
        else:
            train_delimiter = "\t" if output_train_format == "tsv" else ","
            write_tsv_csv(
                args.output_train, header, train_rows, delimiter=train_delimiter
            )
        print(f"  Wrote {len(train_rows)} rows")

        # Write test set
        print(f"Writing test set to {args.output_test}...")
        if output_test_format == "json":
            # Convert to JSON format (list of dicts)
            test_data = [dict(zip(header, row)) for row in test_rows]
            write_json(args.output_test, test_data)
        else:
            test_delimiter = "\t" if output_test_format == "tsv" else ","
            write_tsv_csv(args.output_test, header, test_rows, delimiter=test_delimiter)
        print(f"  Wrote {len(test_rows)} rows")

    elif input_format == "json":
        data = read_json(args.input_file)

        # Handle both list and dict formats
        if isinstance(data, list):
            print(f"  Loaded {len(data)} items")
            train_data, test_data = split_data(
                data, train_size=args.train_size, random_state=args.seed
            )
        elif isinstance(data, dict):
            # For dict, treat top-level keys as items
            items = list(data.items())
            print(f"  Loaded {len(items)} top-level objects")
            train_items, test_items = split_data(
                items, train_size=args.train_size, random_state=args.seed
            )
            train_data = dict(train_items)
            test_data = dict(test_items)
        else:
            raise ValueError(
                "JSON file must contain either a list or a dict at the top level"
            )

        print(f"\nSplit: {len(train_data)} training, {len(test_data)} test")
        if isinstance(data, list):
            print(f"  Training: {len(train_data) / len(data) * 100:.1f}%")
            print(f"  Test: {len(test_data) / len(data) * 100:.1f}%")

        # Write training set
        print(f"\nWriting training set to {args.output_train}...")
        if output_train_format == "json":
            write_json(args.output_train, train_data)
        else:
            # Convert JSON to TSV/CSV
            if (
                isinstance(train_data, list)
                and len(train_data) > 0
                and isinstance(train_data[0], dict)
            ):
                header = list(train_data[0].keys())
                train_rows = [
                    [str(item.get(key, "")) for key in header] for item in train_data
                ]
                train_delimiter = "\t" if output_train_format == "tsv" else ","
                write_tsv_csv(
                    args.output_train, header, train_rows, delimiter=train_delimiter
                )
            else:
                raise ValueError(
                    "Cannot convert JSON structure to TSV/CSV. Expected list of dicts."
                )
        print(f"  Wrote {len(train_data)} items")

        # Write test set
        print(f"Writing test set to {args.output_test}...")
        if output_test_format == "json":
            write_json(args.output_test, test_data)
        else:
            # Convert JSON to TSV/CSV
            if (
                isinstance(test_data, list)
                and len(test_data) > 0
                and isinstance(test_data[0], dict)
            ):
                header = list(test_data[0].keys())
                test_rows = [
                    [str(item.get(key, "")) for key in header] for item in test_data
                ]
                test_delimiter = "\t" if output_test_format == "tsv" else ","
                write_tsv_csv(
                    args.output_test, header, test_rows, delimiter=test_delimiter
                )
            else:
                raise ValueError(
                    "Cannot convert JSON structure to TSV/CSV. Expected list of dicts."
                )
        print(f"  Wrote {len(test_data)} items")

    print("\n✓ Split complete!")


if __name__ == "__main__":
    main()
