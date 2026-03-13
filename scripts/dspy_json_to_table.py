#!/usr/bin/env python3
"""
Convert a classify_dspy_*.json evaluation file to CSV or TSV format matching
the structure of classify_*.csv files.

Format resolution order:
  1. --format flag (if given)
  2. Extension of --output file (.csv or .tsv)
  3. Default: csv

Usage:
    python dspy_json_to_table.py classify_dspy_claude_MIPROv2_gpt4o-mini.json
    python dspy_json_to_table.py classify_dspy_claude_MIPROv2_gpt4o-mini.json --format tsv
    python dspy_json_to_table.py classify_dspy_claude_MIPROv2_gpt4o-mini.json --output results.csv
    python dspy_json_to_table.py classify_dspy_claude_MIPROv2_gpt4o-mini.json --output results.tsv
    python dspy_json_to_table.py classify_dspy_claude_MIPROv2_gpt4o-mini.json --no-print --output results.tsv
    python dspy_json_to_table.py classify_dspy_claude_MIPROv2_gpt4o-mini.json --parse-agent-name
"""

import argparse
import csv
import json
import os
import sys


FIELDNAMES = [
    "agent_name",
    "metric_type",
    "property",
    "class",
    "accuracy",
    "precision",
    "recall",
    "f1_score",
    "support",
    "tp",
    "fp",
    "tn",
    "fn",
]

DELIMITERS = {"csv": ",", "tsv": "\t"}


def resolve_format(fmt: str | None, output_path: str | None) -> str:
    """
    Resolve output format with the following precedence:
      1. --format flag
      2. Extension of --output path
      3. Default: csv
    """
    if fmt is not None:
        return fmt
    if output_path is not None:
        ext = os.path.splitext(output_path)[1].lower().lstrip(".")
        if ext in DELIMITERS:
            return ext
    return "csv"


def parse_agent_name(
    json_path: str, summary: dict, force_from_path: bool = False
) -> str:
    """
    Return the agent_name using the following logic:
      - If force_from_path is True, always derive from the filename.
      - Otherwise use agent_name from the JSON summary if present.
      - Fall back to deriving from the filename if not in the summary.

    Example: classify_dspy_claude_MIPROv2_gpt4o-mini.json -> dspy_claude_MIPROv2_gpt4o-mini
    """
    if not force_from_path and summary.get("agent_name"):
        return summary["agent_name"]

    stem = os.path.splitext(os.path.basename(json_path))[0]
    marker = "dspy_"
    idx = stem.find(marker)
    # if idx != -1: # this would skip the "dspy_"prefix
    #     return stem[idx + len(marker) :]
    return stem[idx:]


def metrics_row(
    agent_name: str, metric_type: str, prop: str, cls: str, m: dict
) -> dict:
    return {
        "agent_name": agent_name,
        "metric_type": metric_type,
        "property": prop,
        "class": cls,
        "accuracy": m.get("accuracy", ""),
        "precision": m.get("precision", ""),
        "recall": m.get("recall", ""),
        "f1_score": m.get("f1_score", ""),
        "support": m.get("support", ""),
        "tp": m.get("tp", ""),
        "fp": m.get("fp", ""),
        "tn": m.get("tn", ""),
        "fn": m.get("fn", ""),
    }


def convert(json_path: str, parse_agent_name_from_path: bool = False) -> list:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = data["evaluation_summary"]
    agent_name = parse_agent_name(
        json_path, summary, force_from_path=parse_agent_name_from_path
    )

    rows = []

    # Overall row
    rows.append(
        metrics_row(agent_name, "overall", "all", "all", summary["overall_metrics"])
    )

    # Per-property rows
    for prop, prop_data in summary["per_property_metrics"].items():
        # macro_avg row
        rows.append(
            metrics_row(agent_name, "macro_avg", prop, "all", prop_data["macro_avg"])
        )
        # per_class rows
        for cls, cls_data in prop_data["per_class"].items():
            rows.append(metrics_row(agent_name, "per_class", prop, cls, cls_data))

    return rows


def write_table(rows: list, output_file, fmt: str) -> None:
    delimiter = DELIMITERS[fmt]
    writer = csv.DictWriter(output_file, fieldnames=FIELDNAMES, delimiter=delimiter)
    writer.writeheader()
    writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Convert a classify_dspy_*.json file to CSV or TSV."
    )
    parser.add_argument("input", help="Path to the classify_dspy_*.json file")
    parser.add_argument(
        "--format",
        dest="fmt",
        choices=["csv", "tsv"],
        default=None,
        help="Output format: csv or tsv. If omitted, inferred from --output extension, defaulting to csv.",
    )
    parser.add_argument(
        "--print",
        dest="print_output",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Print output to stdout (default: true)",
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        default=None,
        help="Optional path to save the output file (.csv or .tsv)",
    )
    parser.add_argument(
        "--parse-agent-name",
        dest="parse_agent_name",
        action="store_true",
        default=False,
        help="Always derive agent_name from the input filename, ignoring the value in the JSON.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    fmt = resolve_format(args.fmt, args.output_path)
    rows = convert(args.input, parse_agent_name_from_path=args.parse_agent_name)

    if args.print_output:
        write_table(rows, sys.stdout, fmt)

    if args.output_path:
        with open(args.output_path, "w", newline="", encoding="utf-8") as f:
            write_table(rows, f, fmt)
        if not args.print_output:
            print(f"Saved to {args.output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
