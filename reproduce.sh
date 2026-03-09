#!/bin/bash
# llm-clean Reproduction Script
# Reproduces all results from the paper.
#
# Usage:
#   bash reproduce.sh [--all] [--static] [--guarino-repro] [--zeroshot] [--agentic] [--multi-critic]
#
# Flags (default: --all if no flags are given):
#   --static        Step 1: download the Guarino & Welty paper and generate the messy OWL
#   --guarino-repro Step 2: LLM meta-property analysis on the Guarino & Welty taxonomy
#   --zeroshot      Step 3: zero-shot taxonomy benchmark (13 models x 10 domains)
#   --agentic       Step 4: agentic single-critic benchmark (3 small models)
#   --multi-critic  Step 5: multi-critic benchmark (3 models x 3 critic conditions)
#   --all           Run all steps (default)
#
# The OPENROUTER_API_KEY environment variable must be set for steps 2-5.
# Do NOT put the key inside this script or the Docker image; pass it at runtime:
#
#   OPENROUTER_API_KEY=sk-xxx bash reproduce.sh --all
#   docker run --rm -e OPENROUTER_API_KEY=sk-xxx -v $(pwd)/output:/app/output llm-clean
#
set -euo pipefail

# ---------------------------------------------------------------------------
# Parse flags
# ---------------------------------------------------------------------------
RUN_STATIC=false
RUN_GUARINO_REPRO=false
RUN_ZEROSHOT=false
RUN_AGENTIC=false
RUN_MULTI_CRITIC=false

if [ $# -eq 0 ]; then
    RUN_STATIC=true
    RUN_GUARINO_REPRO=true
    RUN_ZEROSHOT=true
    RUN_AGENTIC=true
    RUN_MULTI_CRITIC=true
fi

for arg in "$@"; do
    case $arg in
        --all)
            RUN_STATIC=true
            RUN_GUARINO_REPRO=true
            RUN_ZEROSHOT=true
            RUN_AGENTIC=true
            RUN_MULTI_CRITIC=true
            ;;
        --static)        RUN_STATIC=true ;;
        --guarino-repro) RUN_GUARINO_REPRO=true ;;
        --zeroshot)      RUN_ZEROSHOT=true ;;
        --agentic)       RUN_AGENTIC=true ;;
        --multi-critic)  RUN_MULTI_CRITIC=true ;;
        *)
            echo "Unknown flag: $arg"
            echo "Usage: $0 [--all] [--static] [--guarino-repro] [--zeroshot] [--agentic] [--multi-critic]"
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Environment setup
# ---------------------------------------------------------------------------
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"

DATASET="data/benchmark_10_domains.json"
OWL="output/ontologies/guarino_messy.owl"
PAPER_PDF="data/raw/01-guarino00formal.pdf"
PAPER_TXT="resources/converted_text_files/guarino_text_files/01-guarino00formal-converted-corrected.txt"

mkdir -p data/raw output/ontologies output/experiments output/analyzed_entities \
         output/evaluation_results docs/reports

need_api_key() {
    if [ -z "${OPENROUTER_API_KEY:-}" ]; then
        echo "ERROR: OPENROUTER_API_KEY is not set. Steps 2-5 require an API key."
        echo "Pass it as: OPENROUTER_API_KEY=sk-xxx bash reproduce.sh $*"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Step 1: Static reproduction — Guarino & Welty messy taxonomy
# ---------------------------------------------------------------------------
if $RUN_STATIC; then
    echo ""
    echo "====================================================================="
    echo "Step 1: Static reproduction (Guarino & Welty messy taxonomy)"
    echo "====================================================================="

    echo ">>> Downloading Guarino & Welty (2000) paper..."
    uv run python scripts/download_paper.py \
        --url "http://cui.unige.ch/isi/cours/aftsi/articles/01-guarino00formal.pdf" \
        --output "$PAPER_PDF"

    echo ">>> Generating messy taxonomy OWL from Figure 2..."
    uv run python scripts/generate_messy_owl.py --output "$OWL"

    echo "Step 1 complete. OWL: $OWL"
fi

# ---------------------------------------------------------------------------
# Step 2: Guarino & Welty meta-property reproduction
# ---------------------------------------------------------------------------
if $RUN_GUARINO_REPRO; then
    need_api_key
    echo ""
    echo "====================================================================="
    echo "Step 2: Guarino & Welty meta-property analysis (Table 2 in paper)"
    echo "====================================================================="

    # 2a. Single-prompt, no background — Claude
    echo ">>> Claude: single-prompt, no background..."
    uv run python scripts/batch_analyze_owl.py "$OWL" \
        --model anthropic \
        --output output/analyzed_entities/analyzed_entities_claude_no_files.tsv

    # 2b. Single-prompt, with corrected paper text — Claude
    echo ">>> Claude: single-prompt, with full paper text..."
    uv run python scripts/batch_analyze_owl.py "$OWL" \
        --model anthropic \
        --background-file "$PAPER_TXT" \
        --output output/analyzed_entities/analyzed_entities_claude_corrected_text.tsv

    # 2c. Single-prompt, no background — Gemini
    echo ">>> Gemini: single-prompt, no background..."
    uv run python scripts/batch_analyze_owl.py "$OWL" \
        --model gemini \
        --output output/analyzed_entities/analyzed_entities_gemini_no_files.tsv

    # 2d. Agent-based, no background files — Claude
    echo ">>> Claude agents: no background files..."
    uv run python scripts/batch_analyze_owl_agents.py "$OWL" \
        --model anthropic \
        --no-default-backgrounds \
        --output output/analyzed_entities/analyzed_entities_claude_agents_no_files.tsv

    # 2e. Agent-based, with per-property background files — Claude
    echo ">>> Claude agents: with per-property background files..."
    uv run python scripts/batch_analyze_owl_agents.py "$OWL" \
        --model anthropic \
        --output output/analyzed_entities/analyzed_entities_claude_agents_using_files_no_intro.tsv

    # 2f. Agent-based, with per-property files + introduction — Claude
    echo ">>> Claude agents: with per-property files + introduction..."
    uv run python scripts/batch_analyze_owl_agents.py "$OWL" \
        --model anthropic \
        --with-intro \
        --output output/analyzed_entities/analyzed_entities_claude_agents_using_files_with_intro.tsv

    # 2g. Evaluate all against ground truth
    echo ">>> Evaluating all configurations against ground truth..."
    for TSV in output/analyzed_entities/analyzed_entities_claude*.tsv \
                output/analyzed_entities/analyzed_entities_gemini*.tsv; do
        [ -f "$TSV" ] || continue
        echo "    Evaluating: $TSV"
        uv run python scripts/evaluate_analysis.py "$TSV" resources/ground_truth.tsv \
            > "${TSV%.tsv}_eval.txt" 2>&1 || true
    done

    echo "Step 2 complete. Results in output/analyzed_entities/"
fi

# ---------------------------------------------------------------------------
# Step 3: Zero-shot taxonomy benchmark (13 models)
# ---------------------------------------------------------------------------
if $RUN_ZEROSHOT; then
    need_api_key
    echo ""
    echo "====================================================================="
    echo "Step 3: Zero-shot taxonomy benchmark (13 models x 10 domains)"
    echo "====================================================================="
    echo "WARNING: This runs 13 models and may take several hours."

    uv run python scripts/run_benchmark.py

    echo "Step 3 complete. Reports in output/experiments/"
fi

# ---------------------------------------------------------------------------
# Step 4: Agentic single-critic benchmark (3 small models)
# ---------------------------------------------------------------------------
if $RUN_AGENTIC; then
    need_api_key
    echo ""
    echo "====================================================================="
    echo "Step 4: Agentic single-critic benchmark (3 models x 10 domains)"
    echo "====================================================================="

    uv run python scripts/run_agentic_benchmark.py

    echo "Step 4 complete. Reports in output/experiments/"
fi

# ---------------------------------------------------------------------------
# Step 5: Multi-critic benchmark (3 models x 3 critic conditions)
# ---------------------------------------------------------------------------
if $RUN_MULTI_CRITIC; then
    need_api_key
    echo ""
    echo "====================================================================="
    echo "Step 5: Multi-critic benchmark (3 models x 3 conditions)"
    echo "Single-critic vs. multi-critic (t=2 majority, t=1 strict)"
    echo "====================================================================="
    echo "WARNING: Each multi-critic run makes 4x more API calls than single-critic."

    SMALL_MODELS=(
        "meta-llama/llama-3.2-3b-instruct"
        "meta-llama/llama-3.1-8b-instruct"
        "qwen/qwen-2.5-7b-instruct"
    )

    for MODEL in "${SMALL_MODELS[@]}"; do
        SLUG=$(echo "$MODEL" | cut -d'/' -f2)
        echo ""
        echo "--- Model: $SLUG ---"

        # Single-critic (may already exist from Step 4; script skips if output exists)
        echo ">>> Single-critic..."
        uv run python scripts/agentic_taxonomy.py "$DATASET" \
            "output/experiments/taxonomy_agentic_${SLUG}.json" \
            --model "$MODEL"

        # Multi-critic, majority threshold (t=2)
        echo ">>> Multi-critic (t=2, majority)..."
        uv run python scripts/agentic_taxonomy_multi_critic.py "$DATASET" \
            "output/experiments/taxonomy_agentic_multi_critic_${SLUG}.json" \
            --model "$MODEL" --threshold 2

        # Multi-critic, strict threshold (t=1)
        echo ">>> Multi-critic (t=1, strict)..."
        uv run python scripts/agentic_taxonomy_multi_critic.py "$DATASET" \
            "output/experiments/taxonomy_agentic_multi_critic_t1_${SLUG}.json" \
            --model "$MODEL" --threshold 1
    done

    echo ""
    echo ">>> Evaluating all conditions and generating comparison report..."
    uv run python scripts/run_multi_critic_benchmark.py
    echo "Report: output/experiments/MULTI_CRITIC_BENCHMARK_REPORT.md"

    echo "Step 5 complete."
fi

echo ""
echo "====================================================================="
echo "Reproduction complete."
echo "All outputs are in output/ and docs/reports/."
echo "====================================================================="
