#!/bin/bash
set -e

# Configuration
OWL_FILE="output/ontologies/guarino_messy.owl"
TEXT_BG="data/raw/converted_text_files/guarino_text_files/01-guarino00formal-converted.txt"
GT_FILE="data/raw/ground_truth.tsv"

# Model List (Name|ID|Slug)
MODELS=(
    "Gemini 2.5 Flash|google/gemini-2.5-flash|gemini_2.5_flash"
    "Claude 3.5 Sonnet|anthropic/claude-3.5-sonnet|claude_3.5_sonnet"
    "GPT-4o|openai/gpt-4o|gpt-4o"
    "Llama 3.3 70B|meta-llama/llama-3.3-70b-instruct|llama_3.3_70b"
    "Llama 3.2 3B|meta-llama/llama-3.2-3b-instruct|llama_3.2_3b"
    "Mistral Large|mistralai/mistral-large-2411|mistral_large"
    "Qwen 2.5 72B|qwen/qwen-2.5-72b-instruct|qwen_2.5_72b"
    "DeepSeek V3|deepseek/deepseek-chat|deepseek_v3"
    "Llama 3.1 8B|meta-llama/llama-3.1-8b-instruct|llama_3.1_8b"
    "Gemini 2.0 Flash Lite|google/gemini-2.0-flash-lite-001|gemini_2.0_flash_lite"
    "Gemini 2.5 Flash Lite|google/gemini-2.5-flash-lite|gemini_2.5_flash_lite"
    "Qwen 2.5 7B|qwen/qwen-2.5-7b-instruct|qwen_2.5_7b"
    "Gemma 2 9B|google/gemma-2-9b-it|gemma_2_9b"
)

# Function to run analysis and evaluation
run_eval() {
    local name=$1
    local id=$2
    local slug=$3
    local config=$4 # "no-files" or "text"

    local output_tsv="output/analyzed_entities/analyzed_entities_${slug}_${config}.tsv"
    local output_json="output/evaluation_results/evaluate_${slug}_${config}.json"
    
    echo ">>> Running $name ($config)..."

    # Analysis
    if [ "$config" == "text" ]; then
        uv run python scripts/batch_analyze_owl.py "$OWL_FILE" --model "$id" --background-file "$TEXT_BG" --output "$output_tsv"
    else
        uv run python scripts/batch_analyze_owl.py "$OWL_FILE" --model "$id" --output "$output_tsv"
    fi

    # Evaluation
    uv run python scripts/evaluate_analysis.py "$output_tsv" "$GT_FILE" --agent-name "$name" --output "$output_json"
}

# Run all (Sequentially for reproducibility/rate-limiting)
for model in "${MODELS[@]}"; do
    IFS='|' read -r name id slug <<< "$model"
    run_eval "$name" "$id" "$slug" "no-files"
    run_eval "$name" "$id" "$slug" "text"
done

# Aggregation
echo ">>> Aggregating expanded results..."

# Original files
FILES=(
    "output/evaluation_results/evaluate_claude_no_files.json"
    "output/evaluation_results/evaluate_claude_pdf.json"
    "output/evaluation_results/evaluate_claude_text.json"
    "output/evaluation_results/evaluate_claude_corrected_text.json"
    "output/evaluation_results/evaluate_gemini_no_files.json"
    "output/evaluation_results/evaluate_gemini_pdf.json"
    "output/evaluation_results/evaluate_gemini_text.json"
    "output/evaluation_results/evaluate_gemini_corrected_text.json"
)
INDEXES=(
    "no-files (anthropic)"
    "pdf (anthropic)"
    "text (anthropic)"
    "corrected (anthropic)"
    "no-files (gemini)"
    "pdf (gemini)"
    "text (gemini)"
    "corrected (gemini)"
)

# New files
for model in "${MODELS[@]}"; do
    IFS='|' read -r name id slug <<< "$model"
    FILES+=("output/evaluation_results/evaluate_${slug}_no-files.json")
    INDEXES+=("no-files ($name)")
    FILES+=("output/evaluation_results/evaluate_${slug}_text.json")
    INDEXES+=("text ($name)")
done

uv run python scripts/collect_evaluations.py --files "${FILES[@]}" --indexes "${INDEXES[@]}" --output output/collect_non_agent_results.md

# Copy to final location
cp output/collect_non_agent_results.md docs/reports/NON_AGENT_BATCH_ANALYSIS_REPORT.md

echo ">>> Aggregated report updated at docs/reports/NON_AGENT_BATCH_ANALYSIS_REPORT.md"
