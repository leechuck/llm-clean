import os
import sys
import subprocess
import pandas as pd

# Add current directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from evaluate_taxonomy import load_data, evaluate_domain

DATASET_FILE = "data/benchmark_10_domains.json"
MODELS = {
    "Llama 3.2 3B": "meta-llama/llama-3.2-3b-instruct",
    "Llama 3.1 8B": "meta-llama/llama-3.1-8b-instruct",
    "Qwen 2.5 7B": "qwen/qwen-2.5-7b-instruct",
}

# Experiment conditions: (label, script, file_template, extra_args)
# file_template uses {slug} for model slug
CONDITIONS = [
    {
        "label": "Single",
        "script": "scripts/agentic_taxonomy.py",
        "file_tpl": "output/experiments/taxonomy_agentic_{slug}.json",
        "extra_args": [],
    },
    {
        "label": "Multi-strict (t=1)",
        "script": "scripts/agentic_taxonomy_multi_critic.py",
        "file_tpl": "output/experiments/taxonomy_agentic_multi_critic_t1_{slug}.json",
        "extra_args": ["--threshold", "1"],
    },
    {
        "label": "Multi-majority (t=2)",
        "script": "scripts/agentic_taxonomy_multi_critic.py",
        "file_tpl": "output/experiments/taxonomy_agentic_multi_critic_{slug}.json",
        "extra_args": ["--threshold", "2"],
    },
]


def evaluate_results(dataset_file, taxonomy_file):
    try:
        data, tax, _ = load_data(dataset_file, taxonomy_file)

        total_links = 0
        total_cycles = 0
        total_violations = 0
        total_warnings = 0

        for domain in data:
            if domain in tax:
                stats = evaluate_domain(domain, data[domain], tax[domain])
                total_links += stats["links_count"]
                total_cycles += len(stats["cycles"])
                total_violations += len(stats["violations"])
                total_warnings += len(stats["warnings"])

        return {
            "total_links": total_links,
            "total_cycles": total_cycles,
            "total_violations": total_violations,
            "total_warnings": total_warnings,
        }
    except Exception as e:
        print(f"Error evaluating {taxonomy_file}: {e}")
        return None


def run_experiment(script, dataset_file, output_file, model_id, extra_args=None):
    """Run a taxonomy generation script, skip if output already exists."""
    if os.path.exists(output_file):
        print(f"  Reusing existing results: {output_file}")
        return True

    cmd = [sys.executable, script, dataset_file, output_file, "--model", model_id]
    if extra_args:
        cmd.extend(extra_args)
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Error running {script}: {e}")
        return False


def main():
    os.makedirs("output/experiments", exist_ok=True)

    results = []

    for friendly_name, model_id in MODELS.items():
        model_slug = model_id.split("/")[-1]

        for cond in CONDITIONS:
            output_file = cond["file_tpl"].format(slug=model_slug)
            print(f"\n>>> {cond['label']}: {friendly_name}")
            if run_experiment(
                cond["script"], DATASET_FILE, output_file, model_id, cond["extra_args"]
            ):
                stats = evaluate_results(DATASET_FILE, output_file)
                if stats:
                    results.append(
                        {
                            "Model": friendly_name,
                            "Critic Type": cond["label"],
                            "Total Links": stats["total_links"],
                            "Violations": stats["total_violations"],
                            "Cycles": stats["total_cycles"],
                            "Warnings": stats["total_warnings"],
                        }
                    )

    # --- Generate report ---
    if not results:
        print("\nNo results to report.")
        return

    df = pd.DataFrame(results)
    print("\n" + "=" * 60)
    print("Multi-Critic Benchmark Results")
    print("=" * 60)
    print(df.to_markdown(index=False))

    # Summary: compute deltas vs single-critic baseline per model
    summary_rows = []
    for friendly_name in MODELS:
        single = next(
            (r for r in results if r["Model"] == friendly_name and r["Critic Type"] == "Single"),
            None,
        )
        if not single:
            continue
        for cond in CONDITIONS[1:]:  # skip Single itself
            multi = next(
                (r for r in results if r["Model"] == friendly_name and r["Critic Type"] == cond["label"]),
                None,
            )
            if multi:
                summary_rows.append(
                    {
                        "Model": friendly_name,
                        "Comparison": f"{cond['label']} vs Single",
                        "Single Links": single["Total Links"],
                        "Multi Links": multi["Total Links"],
                        "Delta Violations": multi["Violations"] - single["Violations"],
                        "Delta Cycles": multi["Cycles"] - single["Cycles"],
                        "Delta Warnings": multi["Warnings"] - single["Warnings"],
                    }
                )

    report_path = "output/experiments/MULTI_CRITIC_BENCHMARK_REPORT.md"
    with open(report_path, "w") as f:
        f.write("# Multi-Critic vs Single-Critic Benchmark\n\n")
        f.write("## Full Results\n\n")
        f.write(df.to_markdown(index=False))
        f.write("\n\n")

        if summary_rows:
            sdf = pd.DataFrame(summary_rows)
            f.write("## Summary (Deltas vs Single-Critic baseline, negative = improvement)\n\n")
            f.write(sdf.to_markdown(index=False))
            f.write("\n")

    print(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    main()
