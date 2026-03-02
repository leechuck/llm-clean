#!/bin/bash
set -e

# llm-clean Reproduction Script
# Orchestrates the reproduction of the paper's results.

# 1. Environment Check
if [ ! -f .env ]; then
    echo "Warning: .env file not found. API-based benchmarks will fail."
    echo "Please create a .env file with OPENROUTER_API_KEY."
fi

# Ensure src is in PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# 2. Guarino & Welty (2000) Static Reproduction
echo "--- Step 1: Reproducing Guarino & Welty (2000) Taxonomy ---"

mkdir -p data/raw output/ontologies output/experiments docs/reports

echo "Downloading paper..."
uv run scripts/download_paper.py --url "http://cui.unige.ch/isi/cours/aftsi/articles/01-guarino00formal.pdf" --output "data/raw/01-guarino00formal.pdf"

echo "Generating messy taxonomy OWL..."
uv run --with rdflib scripts/generate_messy_owl.py --output "output/ontologies/guarino_messy.owl"

echo "Static reproduction complete. Results in output/ontologies/guarino_messy.owl"

# 3. LLM Benchmarks (Optional)
echo ""
echo "--- Step 2: LLM Benchmarks ---"

if grep -q "OPENROUTER_API_KEY" .env 2>/dev/null; then
    read -p "Do you want to run the zero-shot benchmark? (y/N) " run_bench
    if [[ $run_bench == "y" || $run_bench == "Y" ]]; then
        uv run scripts/run_benchmark.py
    fi

    read -p "Do you want to run the agentic benchmark? (y/N) " run_agentic
    if [[ $run_agentic == "y" || $run_agentic == "Y" ]]; then
        uv run scripts/run_agentic_benchmark.py
    fi
else
    echo "Skipping LLM benchmarks (no API key in .env)."
    echo "Existing reports in docs/reports/."
fi

echo ""
echo "Reproduction process finished."
