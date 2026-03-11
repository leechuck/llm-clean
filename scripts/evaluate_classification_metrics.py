import argparse
import csv
import sys
import os
import json
from collections import defaultdict
from pathlib import Path


def normalize_property(prop):
    """Normalize property strings (e.g., handles whitespace)."""
    if not prop:
        return "N/A"
    return prop.strip()


def load_tsv(path):
    data = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                term = row.get("term")
                if term:
                    data[term] = row
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    return data


def calculate_metrics_per_class(true_positives, false_positives, false_negatives):
    """Calculate precision, recall, and F1-score given TP, FP, FN."""
    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0.0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 0.0
    )
    f1 = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return precision, recall, f1


def calculate_classification_metrics(predictions, ground_truth, meta_properties):
    """
    Calculate precision, recall, F1-score, and accuracy for each property.
    Returns metrics for each property class and macro-averaged metrics.
    """

    # Track TP, FP, FN for each property value
    property_metrics = {}

    for prop in meta_properties:
        # Get all possible values for this property from ground truth
        possible_values = set()
        for term, gt_row in ground_truth.items():
            val = normalize_property(gt_row.get(prop))
            if val != "N/A":
                possible_values.add(val)

        # Initialize counters for each value
        class_counts = {}
        for val in possible_values:
            class_counts[val] = {
                "tp": 0,  # True Positives
                "fp": 0,  # False Positives
                "tn": 0,  # True Negatives
                "fn": 0,  # False Negatives
            }

        # Count TP, FP, FN, TN for each term in ground truth
        for term, gt_row in ground_truth.items():
            g_val = normalize_property(gt_row.get(prop))

            # Skip if not in predictions or has error
            if term not in predictions or predictions[term].get("error"):
                # Count as False Negative for the ground truth class
                if g_val in class_counts:
                    class_counts[g_val]["fn"] += 1
                continue

            p_val = normalize_property(predictions[term].get(prop))

            # Update counts for each class
            for val in possible_values:
                if g_val == val and p_val == val:
                    # Correctly predicted this class
                    class_counts[val]["tp"] += 1
                elif g_val != val and p_val != val:
                    # Correctly predicted NOT this class
                    class_counts[val]["tn"] += 1
                elif g_val == val and p_val != val:
                    # Should have predicted this class but didn't
                    class_counts[val]["fn"] += 1
                elif g_val != val and p_val == val:
                    # Predicted this class but shouldn't have
                    class_counts[val]["fp"] += 1

        # Calculate metrics for each class
        property_metrics[prop] = {"per_class": {}, "macro_avg": {}, "support": {}}

        total_precision = 0
        total_recall = 0
        total_f1 = 0
        valid_classes = 0

        for val in possible_values:
            counts = class_counts[val]
            precision, recall, f1 = calculate_metrics_per_class(
                counts["tp"], counts["fp"], counts["fn"]
            )

            support = (
                counts["tp"] + counts["fn"]
            )  # Total instances of this class in ground truth

            # Calculate accuracy for this class: (TP + TN) / (TP + TN + FP + FN)
            class_total = counts["tp"] + counts["tn"] + counts["fp"] + counts["fn"]
            class_accuracy = (
                (counts["tp"] + counts["tn"]) / class_total if class_total > 0 else 0.0
            )

            property_metrics[prop]["per_class"][val] = {
                "accuracy": class_accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "support": support,
                "tp": counts["tp"],
                "fp": counts["fp"],
                "tn": counts["tn"],
                "fn": counts["fn"],
            }

            property_metrics[prop]["support"][val] = support

            # For macro average (only count classes with support > 0)
            if support > 0:
                total_precision += precision
                total_recall += recall
                total_f1 += f1
                valid_classes += 1

        # Macro-averaged metrics and aggregate counts
        total_support = sum(
            class_counts[val]["tp"] + class_counts[val]["fn"] for val in possible_values
        )
        total_tp = sum(class_counts[val]["tp"] for val in possible_values)
        total_fp = sum(class_counts[val]["fp"] for val in possible_values)
        total_tn = sum(class_counts[val]["tn"] for val in possible_values)
        total_fn = sum(class_counts[val]["fn"] for val in possible_values)

        # Calculate accuracy for macro_avg: (TP + TN) / (TP + TN + FP + FN)
        macro_total = total_tp + total_tn + total_fp + total_fn
        macro_accuracy = (total_tp + total_tn) / macro_total if macro_total > 0 else 0.0

        if valid_classes > 0:
            property_metrics[prop]["macro_avg"] = {
                "accuracy": macro_accuracy,
                "precision": total_precision / valid_classes,
                "recall": total_recall / valid_classes,
                "f1_score": total_f1 / valid_classes,
                "support": total_support,
                "tp": total_tp,
                "fp": total_fp,
                "tn": total_tn,
                "fn": total_fn,
            }
        else:
            property_metrics[prop]["macro_avg"] = {
                "accuracy": macro_accuracy,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "support": total_support,
                "tp": total_tp,
                "fp": total_fp,
                "tn": total_tn,
                "fn": total_fn,
            }

        # Calculate accuracy for this property
        correct = sum(class_counts[val]["tp"] for val in possible_values)
        total = len(ground_truth)
        property_metrics[prop]["accuracy"] = correct / total if total > 0 else 0.0

    return property_metrics


def save_as_json(output_path, data):
    """Save evaluation results as JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_as_csv(
    output_path, property_metrics, meta_properties, overall_metrics, agent_name=None
):
    """Save evaluation results as CSV."""
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        # Write header
        header = [
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
        if agent_name:
            header.insert(0, "agent_name")
        writer.writerow(header)

        # Write overall metrics
        row = [
            "overall",
            "all",
            "all",
            f"{overall_metrics['accuracy']:.2f}",
            f"{overall_metrics['precision']:.2f}",
            f"{overall_metrics['recall']:.2f}",
            f"{overall_metrics['f1_score']:.2f}",
            str(overall_metrics["support"]),
            str(overall_metrics["tp"]),
            str(overall_metrics["fp"]),
            str(overall_metrics["tn"]),
            str(overall_metrics["fn"]),
        ]
        if agent_name:
            row.insert(0, agent_name)
        writer.writerow(row)

        # Write per-property metrics
        for prop in meta_properties:
            metrics = property_metrics[prop]

            # Write macro-averaged metrics for this property
            row = [
                "macro_avg",
                prop,
                "all",
                f"{metrics['macro_avg']['accuracy']:.2f}",
                f"{metrics['macro_avg']['precision']:.2f}",
                f"{metrics['macro_avg']['recall']:.2f}",
                f"{metrics['macro_avg']['f1_score']:.2f}",
                str(metrics["macro_avg"]["support"]),
                str(metrics["macro_avg"]["tp"]),
                str(metrics["macro_avg"]["fp"]),
                str(metrics["macro_avg"]["tn"]),
                str(metrics["macro_avg"]["fn"]),
            ]
            if agent_name:
                row.insert(0, agent_name)
            writer.writerow(row)

            # Write per-class metrics
            for val in sorted(metrics["per_class"].keys()):
                class_metrics = metrics["per_class"][val]
                row = [
                    "per_class",
                    prop,
                    val,
                    f"{class_metrics['accuracy']:.2f}",
                    f"{class_metrics['precision']:.2f}",
                    f"{class_metrics['recall']:.2f}",
                    f"{class_metrics['f1_score']:.2f}",
                    str(class_metrics["support"]),
                    str(class_metrics["tp"]),
                    str(class_metrics["fp"]),
                    str(class_metrics["tn"]),
                    str(class_metrics["fn"]),
                ]
                if agent_name:
                    row.insert(0, agent_name)
                writer.writerow(row)


def save_as_tsv(
    output_path, property_metrics, meta_properties, overall_metrics, agent_name=None
):
    """Save evaluation results as TSV."""
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")

        # Write header
        header = [
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
        if agent_name:
            header.insert(0, "agent_name")
        writer.writerow(header)

        # Write overall metrics
        row = [
            "overall",
            "all",
            "all",
            f"{overall_metrics['accuracy']:.2f}",
            f"{overall_metrics['precision']:.2f}",
            f"{overall_metrics['recall']:.2f}",
            f"{overall_metrics['f1_score']:.2f}",
            str(overall_metrics["support"]),
            str(overall_metrics["tp"]),
            str(overall_metrics["fp"]),
            str(overall_metrics["tn"]),
            str(overall_metrics["fn"]),
        ]
        if agent_name:
            row.insert(0, agent_name)
        writer.writerow(row)

        # Write per-property metrics
        for prop in meta_properties:
            metrics = property_metrics[prop]

            # Write macro-averaged metrics for this property
            row = [
                "macro_avg",
                prop,
                "all",
                f"{metrics['macro_avg']['accuracy']:.2f}",
                f"{metrics['macro_avg']['precision']:.2f}",
                f"{metrics['macro_avg']['recall']:.2f}",
                f"{metrics['macro_avg']['f1_score']:.2f}",
                str(metrics["macro_avg"]["support"]),
                str(metrics["macro_avg"]["tp"]),
                str(metrics["macro_avg"]["fp"]),
                str(metrics["macro_avg"]["tn"]),
                str(metrics["macro_avg"]["fn"]),
            ]
            if agent_name:
                row.insert(0, agent_name)
            writer.writerow(row)

            # Write per-class metrics
            for val in sorted(metrics["per_class"].keys()):
                class_metrics = metrics["per_class"][val]
                row = [
                    "per_class",
                    prop,
                    val,
                    f"{class_metrics['accuracy']:.2f}",
                    f"{class_metrics['precision']:.2f}",
                    f"{class_metrics['recall']:.2f}",
                    f"{class_metrics['f1_score']:.2f}",
                    str(class_metrics["support"]),
                    str(class_metrics["tp"]),
                    str(class_metrics["fp"]),
                    str(class_metrics["tn"]),
                    str(class_metrics["fn"]),
                ]
                if agent_name:
                    row.insert(0, agent_name)
                writer.writerow(row)


def save_as_markdown(
    output_path,
    property_metrics,
    meta_properties,
    overall_metrics,
    ground_truth_file,
    prediction_file,
    total_terms,
    agent_name=None,
):
    """Save evaluation results as Markdown."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Classification Metrics Evaluation\n\n")
        f.write(f"**Ground Truth File:** `{ground_truth_file}`\n\n")
        f.write(f"**Prediction File:** `{prediction_file}`\n\n")
        f.write(f"**Total Ground Truth Terms:** {total_terms}\n\n")

        if agent_name:
            f.write(f"**Agent Name:** {agent_name}\n\n")

        f.write("## Overall Metrics\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Accuracy | {overall_metrics['accuracy']:.2f} |\n")
        f.write(f"| Precision | {overall_metrics['precision']:.2f} |\n")
        f.write(f"| Recall | {overall_metrics['recall']:.2f} |\n")
        f.write(f"| F1-Score | {overall_metrics['f1_score']:.2f} |\n\n")

        f.write("## Per-Property Metrics\n\n")

        for prop in meta_properties:
            metrics = property_metrics[prop]
            prop_name = prop.replace("_", " ").title()

            f.write(f"### {prop_name}\n\n")
            f.write(f"**Accuracy:** {metrics['accuracy']:.2f}\n\n")
            f.write(f"**Macro-Averaged Metrics:**\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Precision | {metrics['macro_avg']['precision']:.2f} |\n")
            f.write(f"| Recall | {metrics['macro_avg']['recall']:.2f} |\n")
            f.write(f"| F1-Score | {metrics['macro_avg']['f1_score']:.2f} |\n\n")

            f.write(f"**Per-Class Metrics:**\n\n")
            f.write(
                "| Class | Precision | Recall | F1-Score | Support | TP | FP | TN | FN |\n"
            )
            f.write(
                "|-------|-----------|--------|----------|---------|----|----|----|----|----|\n"
            )

            for val in sorted(metrics["per_class"].keys()):
                class_metrics = metrics["per_class"][val]
                f.write(
                    f"| {val} | {class_metrics['precision']:.2f} | "
                    f"{class_metrics['recall']:.2f} | "
                    f"{class_metrics['f1_score']:.2f} | "
                    f"{class_metrics['support']} | "
                    f"{class_metrics['tp']} | "
                    f"{class_metrics['fp']} | "
                    f"{class_metrics['tn']} | "
                    f"{class_metrics['fn']} |\n"
                )
            f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate ontological analysis with classification metrics (precision, recall, F1-score, accuracy)."
    )
    parser.add_argument("prediction_file", help="Path to the prediction TSV file.")
    parser.add_argument("ground_truth_file", help="Path to the ground truth TSV file.")
    parser.add_argument(
        "--output",
        "-o",
        help="Path to save evaluation results (format determined by extension: .json, .csv, .tsv, .md)",
    )
    parser.add_argument(
        "--agent-name",
        help="Adds an 'agent_name' column to the output with the specified value (optional)",
    )

    args = parser.parse_args()

    predictions = load_tsv(args.prediction_file)
    ground_truth = load_tsv(args.ground_truth_file)

    meta_properties = ["rigidity", "identity", "own_identity", "unity", "dependence"]

    # Calculate classification metrics
    property_metrics = calculate_classification_metrics(
        predictions, ground_truth, meta_properties
    )

    # Print results
    print("=" * 80)
    print("Classification Metrics Evaluation")
    print("=" * 80)
    print(f"Ground Truth File: {args.ground_truth_file}")
    print(f"Prediction File: {args.prediction_file}")
    print(f"Total Ground Truth Terms: {len(ground_truth)}")

    if args.agent_name:
        print(f"Agent Name: {args.agent_name}")

    print("\n" + "=" * 80)

    # Overall macro-averaged metrics across all properties
    overall_precision = 0
    overall_recall = 0
    overall_f1 = 0
    overall_accuracy = 0
    overall_support = 0
    overall_tp = 0
    overall_fp = 0
    overall_tn = 0
    overall_fn = 0

    for prop in meta_properties:
        metrics = property_metrics[prop]

        print(f"\n{prop.upper().replace('_', ' ')}")
        print("-" * 80)
        print(f"  Accuracy: {metrics['accuracy']:.2f} ({metrics['accuracy']:.2%})")
        print(f"\n  Macro-Averaged Metrics:")
        print(f"    Precision: {metrics['macro_avg']['precision']:.2f}")
        print(f"    Recall:    {metrics['macro_avg']['recall']:.2f}")
        print(f"    F1-Score:  {metrics['macro_avg']['f1_score']:.2f}")

        print(f"\n  Per-Class Metrics:")
        for val in sorted(metrics["per_class"].keys()):
            class_metrics = metrics["per_class"][val]
            print(
                f"    {val:>3} - Precision: {class_metrics['precision']:.2f}, "
                f"Recall: {class_metrics['recall']:.2f}, "
                f"F1: {class_metrics['f1_score']:.2f}, "
                f"Support: {class_metrics['support']}"
            )

        # Accumulate for overall metrics
        overall_precision += metrics["macro_avg"]["precision"]
        overall_recall += metrics["macro_avg"]["recall"]
        overall_f1 += metrics["macro_avg"]["f1_score"]
        overall_accuracy += metrics["accuracy"]
        overall_support += metrics["macro_avg"]["support"]
        overall_tp += metrics["macro_avg"]["tp"]
        overall_fp += metrics["macro_avg"]["fp"]
        overall_tn += metrics["macro_avg"]["tn"]
        overall_fn += metrics["macro_avg"]["fn"]

    # Calculate overall averages
    num_properties = len(meta_properties)
    overall_precision /= num_properties
    overall_recall /= num_properties
    overall_f1 /= num_properties
    # Recalculate overall accuracy using aggregated confusion matrix values
    overall_total = overall_tp + overall_tn + overall_fp + overall_fn
    overall_accuracy = (
        (overall_tp + overall_tn) / overall_total if overall_total > 0 else 0.0
    )

    print("\n" + "=" * 80)
    print("OVERALL METRICS (averaged across all properties)")
    print("=" * 80)
    print(f"  Accuracy:  {overall_accuracy:.2f} ({overall_accuracy:.2%})")
    print(f"  Precision: {overall_precision:.2f}")
    print(f"  Recall:    {overall_recall:.2f}")
    print(f"  F1-Score:  {overall_f1:.2f}")
    print("=" * 80)

    # Save output file if specified
    if args.output:
        output_path = Path(args.output)
        file_ext = output_path.suffix.lower()

        # Prepare overall metrics dictionary
        overall_metrics_dict = {
            "accuracy": round(overall_accuracy, 2),
            "precision": round(overall_precision, 2),
            "recall": round(overall_recall, 2),
            "f1_score": round(overall_f1, 2),
            "support": overall_support,
            "tp": overall_tp,
            "fp": overall_fp,
            "tn": overall_tn,
            "fn": overall_fn,
        }

        if file_ext == ".json":
            # JSON format
            output_data = {
                "evaluation_summary": {
                    "ground_truth_file": args.ground_truth_file,
                    "prediction_file": args.prediction_file,
                    "total_ground_truth_terms": len(ground_truth),
                    "overall_metrics": overall_metrics_dict,
                    "per_property_metrics": {},
                }
            }

            if args.agent_name:
                output_data["evaluation_summary"]["agent_name"] = args.agent_name

            # Add per-property metrics
            for prop in meta_properties:
                metrics = property_metrics[prop]
                output_data["evaluation_summary"]["per_property_metrics"][prop] = {
                    "accuracy": round(metrics["accuracy"], 2),
                    "macro_avg": {
                        "accuracy": round(metrics["macro_avg"]["accuracy"], 2),
                        "precision": round(metrics["macro_avg"]["precision"], 2),
                        "recall": round(metrics["macro_avg"]["recall"], 2),
                        "f1_score": round(metrics["macro_avg"]["f1_score"], 2),
                        "support": metrics["macro_avg"]["support"],
                        "tp": metrics["macro_avg"]["tp"],
                        "fp": metrics["macro_avg"]["fp"],
                        "tn": metrics["macro_avg"]["tn"],
                        "fn": metrics["macro_avg"]["fn"],
                    },
                    "per_class": {},
                }

                for val in metrics["per_class"].keys():
                    class_metrics = metrics["per_class"][val]
                    output_data["evaluation_summary"]["per_property_metrics"][prop][
                        "per_class"
                    ][val] = {
                        "accuracy": round(class_metrics["accuracy"], 2),
                        "precision": round(class_metrics["precision"], 2),
                        "recall": round(class_metrics["recall"], 2),
                        "f1_score": round(class_metrics["f1_score"], 2),
                        "support": class_metrics["support"],
                        "tp": class_metrics["tp"],
                        "fp": class_metrics["fp"],
                        "tn": class_metrics["tn"],
                        "fn": class_metrics["fn"],
                    }

            save_as_json(args.output, output_data)

        elif file_ext == ".csv":
            # CSV format
            save_as_csv(
                args.output,
                property_metrics,
                meta_properties,
                overall_metrics_dict,
                args.agent_name,
            )

        elif file_ext == ".tsv":
            # TSV format
            save_as_tsv(
                args.output,
                property_metrics,
                meta_properties,
                overall_metrics_dict,
                args.agent_name,
            )

        elif file_ext == ".md":
            # Markdown format
            save_as_markdown(
                args.output,
                property_metrics,
                meta_properties,
                overall_metrics_dict,
                args.ground_truth_file,
                args.prediction_file,
                len(ground_truth),
                args.agent_name,
            )
        else:
            print(
                f"\nWarning: Unsupported file extension '{file_ext}'. Supported formats: .json, .csv, .tsv, .md",
                file=sys.stderr,
            )
            print("Saving as JSON format by default.")
            # Default to JSON
            output_data = {
                "evaluation_summary": {
                    "ground_truth_file": args.ground_truth_file,
                    "prediction_file": args.prediction_file,
                    "total_ground_truth_terms": len(ground_truth),
                    "overall_metrics": overall_metrics_dict,
                    "per_property_metrics": {},
                }
            }

            if args.agent_name:
                output_data["evaluation_summary"]["agent_name"] = args.agent_name

            for prop in meta_properties:
                metrics = property_metrics[prop]
                output_data["evaluation_summary"]["per_property_metrics"][prop] = {
                    "accuracy": round(metrics["accuracy"], 2),
                    "macro_avg": {
                        "accuracy": round(metrics["macro_avg"]["accuracy"], 2),
                        "precision": round(metrics["macro_avg"]["precision"], 2),
                        "recall": round(metrics["macro_avg"]["recall"], 2),
                        "f1_score": round(metrics["macro_avg"]["f1_score"], 2),
                        "support": metrics["macro_avg"]["support"],
                        "tp": metrics["macro_avg"]["tp"],
                        "fp": metrics["macro_avg"]["fp"],
                        "tn": metrics["macro_avg"]["tn"],
                        "fn": metrics["macro_avg"]["fn"],
                    },
                    "per_class": {},
                }

                for val in metrics["per_class"].keys():
                    class_metrics = metrics["per_class"][val]
                    output_data["evaluation_summary"]["per_property_metrics"][prop][
                        "per_class"
                    ][val] = {
                        "accuracy": round(class_metrics["accuracy"], 2),
                        "precision": round(class_metrics["precision"], 2),
                        "recall": round(class_metrics["recall"], 2),
                        "f1_score": round(class_metrics["f1_score"], 2),
                        "support": class_metrics["support"],
                        "tp": class_metrics["tp"],
                        "fp": class_metrics["fp"],
                        "tn": class_metrics["tn"],
                        "fn": class_metrics["fn"],
                    }

            save_as_json(args.output, output_data)

        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
