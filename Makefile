.PHONY: help all clean setup directories \
        download-paper generate-owl \
        benchmark-zeroshot benchmark-agentic \
        batch-non-agent batch-non-agent-claude batch-non-agent-gemini \
        batch-agent batch-agent-claude batch-agent-gemini \
        batch-critic batch-critic-claude batch-critic-gemini \
        eval-non-agent eval-non-agent-claude eval-non-agent-gemini \
        eval-agent eval-agent-claude eval-agent-gemini \
        eval-critic eval-critic-claude eval-critic-gemini \
        classify-non-agent classify-non-agent-claude classify-non-agent-gemini \
        classify-agent classify-agent-claude classify-agent-gemini \
        classify-critic classify-critic-claude classify-critic-gemini \
        collect-non-agent collect-agent collect-critic \
        reports reproduce-static reproduce-batch \
        generate-gpt4o-mini-dspy-models generate-llama70b-dspy-models \
        generate-mistral-small-dspy-models generate-mistral7b-dspy-models generate-qwen72b-dspy-models \
        generate-anthropic-dspy-agent-models generate-gemini-dspy-agent-models \
        generate-gemma9b-dspy-agent-models generate-qwen7b-dspy-agent-models \
        generate-llama8b-dspy-agent-models generate-llama3b-dspy-agent-models \
        generate-gpt4o-mini-dspy-agent-models generate-llama70b-dspy-agent-models \
        generate-mistral-small-dspy-agent-models generate-mistral7b-dspy-agent-models generate-qwen72b-dspy-agent-models \
        generate-large-llm-dspy-agent-models generate-small-llm-dspy-agent-models \
        generate-anthropic-dspy-agent-critic-models generate-gemini-dspy-agent-critic-models \
        generate-gemma9b-dspy-agent-critic-models generate-qwen7b-dspy-agent-critic-models \
        generate-llama8b-dspy-agent-critic-models generate-llama3b-dspy-agent-critic-models \
        generate-gpt4o-mini-dspy-agent-critic-models generate-llama70b-dspy-agent-critic-models \
        generate-mistral-small-dspy-agent-critic-models generate-mistral7b-dspy-agent-critic-models generate-qwen72b-dspy-agent-critic-models \
        generate-large-llm-dspy-agent-critic-models generate-small-llm-dspy-agent-critic-models \
        batch-agent-dspy-anthropic-small-models batch-agent-dspy-gemini-small-models \
        batch-agent-dspy-small-models \
        batch-agent-critic-dspy-anthropic-small-models batch-agent-critic-dspy-gemini-small-models \
        batch-agent-critic-dspy-small-models \
        finetune-mistral7b finetune-gemma9b finetune-qwen7b finetune-llama8b finetune-llama3b \
        finetune-all-local \
        test-finetuned-mistral7b test-finetuned-gemma9b test-finetuned-qwen7b \
        test-finetuned-llama8b test-finetuned-llama3b test-finetuned-all

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(BLUE)LLM-Clean Makefile$(NC)"
	@echo "$(YELLOW)Usage: make [target]$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-25s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

all: setup reproduce-static reproduce-batch ## Run complete reproduction pipeline

clean: ## Remove generated files and outputs
	rm -rf output/analyzed_entities/*.tsv
	rm -rf output/evaluation_results/*.json
	rm -rf output/collect_*.tsv output/collect_*.md
	@echo "$(GREEN)Cleaned output files$(NC)"

##@ Setup

setup: directories ## Setup environment and directories
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Warning: .env file not found$(NC)"; \
		echo "Please create a .env file with required API keys"; \
	fi
	@echo "$(GREEN)Setup complete$(NC)"

directories: ## Create required directories
	@mkdir -p data/raw output/ontologies output/analyzed_entities output/evaluation_results output/experiments docs/reports
	@echo "$(GREEN)Directories created$(NC)"

##@ Static Reproduction (reproduce.sh)

reproduce-static: download-paper generate-owl ## Run static Guarino & Welty reproduction
	@echo "$(GREEN)Static reproduction complete$(NC)"

download-paper: directories ## Download Guarino & Welty (2000) paper
	@echo "$(BLUE)Downloading paper...$(NC)"
	uv run scripts/download_paper.py --url "http://cui.unige.ch/isi/cours/aftsi/articles/01-guarino00formal.pdf" --output "data/raw/01-guarino00formal.pdf"

generate-owl: directories ## Generate messy taxonomy OWL file
	@echo "$(BLUE)Generating messy taxonomy OWL...$(NC)"
	uv run --with rdflib scripts/generate_messy_owl.py --output "output/ontologies/guarino_messy.owl"

##@ LLM Benchmarks

benchmark-zeroshot: ## Run zero-shot taxonomy benchmark
	@echo "$(BLUE)Running zero-shot benchmark...$(NC)"
	uv run scripts/run_benchmark.py

benchmark-agentic: ## Run agentic taxonomy benchmark
	@echo "$(BLUE)Running agentic benchmark...$(NC)"
	uv run scripts/run_agentic_benchmark.py

##@ Batch Analysis - Non-Agent (Standard Mode)

batch-non-agent: batch-non-agent-claude batch-non-agent-gemini ## Run all non-agent batch analyses

batch-non-agent-claude: ## Run non-agent batch analysis with Claude (4 configurations)
	@echo "$(BLUE)Running non-agent batch analysis with Claude...$(NC)"
	uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl --model anthropic --output output/analyzed_entities/analyzed_entities_claude_no_files.tsv
	uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl --model anthropic --background-file data/raw/01-guarino00formal.pdf --output output/analyzed_entities/analyzed_entities_claude_pdf.tsv
	uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl --model anthropic --background-file data/raw/converted_text_files/guarino_text_files/01-guarino00formal-converted.txt --output output/analyzed_entities/analyzed_entities_claude_text.tsv
	uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl --model anthropic --background-file data/raw/converted_text_files/guarino_text_files/01-guarino00formal-converted.txt --output output/analyzed_entities/analyzed_entities_claude_corrected_text.tsv

batch-non-agent-gemini: ## Run non-agent batch analysis with Gemini (4 configurations)
	@echo "$(BLUE)Running non-agent batch analysis with Gemini...$(NC)"
	uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl --model gemini --output output/analyzed_entities/analyzed_entities_gemini_no_files.tsv
	uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl --model gemini --background-file data/raw/01-guarino00formal.pdf --output output/analyzed_entities/analyzed_entities_gemini_pdf.tsv
	uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl --model gemini --background-file data/raw/converted_text_files/guarino_text_files/01-guarino00formal-converted.txt --output output/analyzed_entities/analyzed_entities_gemini_text.tsv
	uv run python scripts/batch_analyze_owl.py output/ontologies/guarino_messy.owl --model gemini --background-file data/raw/converted_text_files/guarino_text_files/01-guarino00formal-converted.txt --output output/analyzed_entities/analyzed_entities_gemini_corrected_text.tsv

##@ Batch Analysis - Agent (Property-by-Property)

batch-agent: batch-agent-claude batch-agent-gemini ## Run all agent batch analyses

batch-agent-claude: ## Run agent batch analysis with Claude (3 configurations)
	@echo "$(BLUE)Running agent batch analysis with Claude...$(NC)"
	uv run python scripts/batch_analyze_owl_agents.py output/ontologies/guarino_messy.owl --model anthropic --no-default-backgrounds --output output/analyzed_entities/analyzed_entities_claude_agents_no_files.tsv
	uv run python scripts/batch_analyze_owl_agents.py output/ontologies/guarino_messy.owl --model anthropic --default-background-file-type simple --output output/analyzed_entities/analyzed_entities_claude_agents_using_files_no_intro.tsv
	uv run python scripts/batch_analyze_owl_agents.py output/ontologies/guarino_messy.owl --model anthropic --default-background-file-type augmented --output output/analyzed_entities/analyzed_entities_claude_agents_using_files_with_intro.tsv

batch-agent-gemini: ## Run agent batch analysis with Gemini (3 configurations)
	@echo "$(BLUE)Running agent batch analysis with Gemini...$(NC)"
	uv run python scripts/batch_analyze_owl_agents.py output/ontologies/guarino_messy.owl --model gemini --no-default-backgrounds --output output/analyzed_entities/analyzed_entities_gemini_agents_no_files.tsv
	uv run python scripts/batch_analyze_owl_agents.py output/ontologies/guarino_messy.owl --model gemini --default-background-file-type simple --output output/analyzed_entities/analyzed_entities_gemini_agents_using_files_no_intro.tsv
	uv run python scripts/batch_analyze_owl_agents.py output/ontologies/guarino_messy.owl --model gemini --default-background-file-type augmented --output output/analyzed_entities/analyzed_entities_gemini_agents_using_files_with_intro.tsv

##@ Batch Analysis - Agent with Critic

batch-critic: batch-critic-claude batch-critic-gemini ## Run all agent critic batch analyses

batch-critic-claude: ## Run agent critic batch analysis with Claude (3 configurations)
	@echo "$(BLUE)Running agent critic batch analysis with Claude...$(NC)"
	uv run python scripts/batch_analyze_owl_agents_critic.py output/ontologies/guarino_messy.owl --model anthropic --no-default-backgrounds --max-critique-attempts 3 --output output/analyzed_entities/analyzed_entities_claude_agents_critic_no_files.tsv
	uv run python scripts/batch_analyze_owl_agents_critic.py output/ontologies/guarino_messy.owl --model anthropic --default-background-file-type simple --max-critique-attempts 3 --output output/analyzed_entities/analyzed_entities_claude_agents_critic_using_files_no_intro.tsv
	uv run python scripts/batch_analyze_owl_agents_critic.py output/ontologies/guarino_messy.owl --model anthropic --default-background-file-type augmented --max-critique-attempts 3 --output output/analyzed_entities/analyzed_entities_claude_agents_critic_using_files_with_intro.tsv

batch-critic-gemini: ## Run agent critic batch analysis with Gemini (3 configurations)
	@echo "$(BLUE)Running agent critic batch analysis with Gemini...$(NC)"
	uv run python scripts/batch_analyze_owl_agents_critic.py output/ontologies/guarino_messy.owl --model gemini --no-default-backgrounds --max-critique-attempts 3 --output output/analyzed_entities/analyzed_entities_gemini_agents_critic_no_files.tsv
	uv run python scripts/batch_analyze_owl_agents_critic.py output/ontologies/guarino_messy.owl --model gemini --default-background-file-type simple --max-critique-attempts 3 --output output/analyzed_entities/analyzed_entities_gemini_agents_critic_using_files_no_intro.tsv
	uv run python scripts/batch_analyze_owl_agents_critic.py output/ontologies/guarino_messy.owl --model gemini --default-background-file-type augmented --max-critique-attempts 3 --output output/analyzed_entities/analyzed_entities_gemini_agents_critic_using_files_with_intro.tsv

##@ Evaluation

eval-non-agent: eval-non-agent-claude eval-non-agent-gemini ## Evaluate all non-agent analyses

eval-non-agent-claude: ## Evaluate non-agent Claude analyses (4 evaluations)
	@echo "$(BLUE)Evaluating non-agent Claude analyses...$(NC)"
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_claude_no_files.tsv data/raw/ground_truth.tsv --agent anthropic --output output/evaluation_results/evaluate_claude_no_files.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_claude_pdf.tsv data/raw/ground_truth.tsv --agent anthropic --output output/evaluation_results/evaluate_claude_pdf.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_claude_text.tsv data/raw/ground_truth.tsv --agent anthropic --output output/evaluation_results/evaluate_claude_text.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_claude_corrected_text.tsv data/raw/ground_truth.tsv --agent anthropic --output output/evaluation_results/evaluate_claude_corrected_text.json

eval-non-agent-gemini: ## Evaluate non-agent Gemini analyses (4 evaluations)
	@echo "$(BLUE)Evaluating non-agent Gemini analyses...$(NC)"
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_gemini_no_files.tsv data/raw/ground_truth.tsv --agent gemini --output output/evaluation_results/evaluate_gemini_no_files.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_gemini_pdf.tsv data/raw/ground_truth.tsv --agent gemini --output output/evaluation_results/evaluate_gemini_pdf.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_gemini_text.tsv data/raw/ground_truth.tsv --agent gemini --output output/evaluation_results/evaluate_gemini_text.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_gemini_corrected_text.tsv data/raw/ground_truth.tsv --agent gemini --output output/evaluation_results/evaluate_gemini_corrected_text.json

eval-agent: eval-agent-claude eval-agent-gemini ## Evaluate all agent analyses

eval-agent-claude: ## Evaluate agent Claude analyses (3 evaluations)
	@echo "$(BLUE)Evaluating agent Claude analyses...$(NC)"
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_claude_agents_no_files.tsv data/raw/ground_truth.tsv --agent anthropic --output output/evaluation_results/evaluate_claude_agents_no_files.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_claude_agents_using_files_no_intro.tsv data/raw/ground_truth.tsv --agent anthropic --output output/evaluation_results/evaluate_claude_agents_using_files_no_intro.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_claude_agents_using_files_with_intro.tsv data/raw/ground_truth.tsv --agent anthropic --output output/evaluation_results/evaluate_claude_agents_using_files_with_intro.json

eval-agent-gemini: ## Evaluate agent Gemini analyses (3 evaluations)
	@echo "$(BLUE)Evaluating agent Gemini analyses...$(NC)"
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_gemini_agents_no_files.tsv data/raw/ground_truth.tsv --agent gemini --output output/evaluation_results/evaluate_gemini_agents_no_files.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_gemini_agents_using_files_no_intro.tsv data/raw/ground_truth.tsv --agent gemini --output output/evaluation_results/evaluate_gemini_agents_using_files_no_intro.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_gemini_agents_using_files_with_intro.tsv data/raw/ground_truth.tsv --agent gemini --output output/evaluation_results/evaluate_gemini_agents_using_files_with_intro.json

eval-critic: eval-critic-claude eval-critic-gemini ## Evaluate all agent critic analyses

eval-critic-claude: ## Evaluate agent critic Claude analyses (3 evaluations)
	@echo "$(BLUE)Evaluating agent critic Claude analyses...$(NC)"
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_claude_agents_critic_no_files.tsv data/raw/ground_truth.tsv --agent anthropic --output output/evaluation_results/evaluate_claude_agents_critic_no_files.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_claude_agents_critic_using_files_no_intro.tsv data/raw/ground_truth.tsv --agent anthropic --output output/evaluation_results/evaluate_claude_agents_critic_using_files_no_intro.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_claude_agents_critic_using_files_with_intro.tsv data/raw/ground_truth.tsv --agent anthropic --output output/evaluation_results/evaluate_claude_agents_critic_using_files_with_intro.json

eval-critic-gemini: ## Evaluate agent critic Gemini analyses (3 evaluations)
	@echo "$(BLUE)Evaluating agent critic Gemini analyses...$(NC)"
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_gemini_agents_critic_no_files.tsv data/raw/ground_truth.tsv --agent gemini --output output/evaluation_results/evaluate_gemini_agents_critic_no_files.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_gemini_agents_critic_using_files_no_intro.tsv data/raw/ground_truth.tsv --agent gemini --output output/evaluation_results/evaluate_gemini_agents_critic_using_files_no_intro.json
	uv run python scripts/evaluate_analysis.py output/analyzed_entities/analyzed_entities_gemini_agents_critic_using_files_with_intro.tsv data/raw/ground_truth.tsv --agent gemini --output output/evaluation_results/evaluate_gemini_agents_critic_using_files_with_intro.json

##@ Classification Metrics Evaluation

classify-non-agent: classify-non-agent-claude classify-non-agent-gemini ## Generate classification metrics for all non-agent analyses

classify-non-agent-claude: ## Generate classification metrics for non-agent Claude analyses (4 evaluations)
	@echo "$(BLUE)Generating classification metrics for non-agent Claude analyses...$(NC)"
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_claude_no_files.tsv data/raw/ground_truth.tsv --agent-name anthropic-no-files --output output/evaluation_results/classify_claude_no_files.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_claude_pdf.tsv data/raw/ground_truth.tsv --agent-name anthropic-pdf --output output/evaluation_results/classify_claude_pdf.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_claude_text.tsv data/raw/ground_truth.tsv --agent-name anthropic-text --output output/evaluation_results/classify_claude_text.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_claude_corrected_text.tsv data/raw/ground_truth.tsv --agent-name anthropic-corrected --output output/evaluation_results/classify_claude_corrected_text.csv

classify-non-agent-gemini: ## Generate classification metrics for non-agent Gemini analyses (4 evaluations)
	@echo "$(BLUE)Generating classification metrics for non-agent Gemini analyses...$(NC)"
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_gemini_no_files.tsv data/raw/ground_truth.tsv --agent-name gemini-no-files --output output/evaluation_results/classify_gemini_no_files.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_gemini_pdf.tsv data/raw/ground_truth.tsv --agent-name gemini-pdf --output output/evaluation_results/classify_gemini_pdf.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_gemini_text.tsv data/raw/ground_truth.tsv --agent-name gemini-text --output output/evaluation_results/classify_gemini_text.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_gemini_corrected_text.tsv data/raw/ground_truth.tsv --agent-name gemini-corrected --output output/evaluation_results/classify_gemini_corrected_text.csv

classify-agent: classify-agent-claude classify-agent-gemini ## Generate classification metrics for all agent analyses

classify-agent-claude: ## Generate classification metrics for agent Claude analyses (3 evaluations)
	@echo "$(BLUE)Generating classification metrics for agent Claude analyses...$(NC)"
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_claude_agents_no_files.tsv data/raw/ground_truth.tsv --agent-name anthropic-agents-no-files --output output/evaluation_results/classify_claude_agents_no_files.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_claude_agents_using_files_no_intro.tsv data/raw/ground_truth.tsv --agent-name anthropic-agents-no-intro --output output/evaluation_results/classify_claude_agents_no_intro.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_claude_agents_using_files_with_intro.tsv data/raw/ground_truth.tsv --agent-name anthropic-agents-with-intro --output output/evaluation_results/classify_claude_agents_with_intro.csv

classify-agent-gemini: ## Generate classification metrics for agent Gemini analyses (3 evaluations)
	@echo "$(BLUE)Generating classification metrics for agent Gemini analyses...$(NC)"
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_gemini_agents_no_files.tsv data/raw/ground_truth.tsv --agent-name gemini-agents-no-files --output output/evaluation_results/classify_gemini_agents_no_files.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_gemini_agents_using_files_no_intro.tsv data/raw/ground_truth.tsv --agent-name gemini-agents-no-intro --output output/evaluation_results/classify_gemini_agents_no_intro.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_gemini_agents_using_files_with_intro.tsv data/raw/ground_truth.tsv --agent-name gemini-agents-with-intro --output output/evaluation_results/classify_gemini_agents_with_intro.csv

classify-critic: classify-critic-claude classify-critic-gemini ## Generate classification metrics for all agent critic analyses

classify-critic-claude: ## Generate classification metrics for agent critic Claude analyses (3 evaluations)
	@echo "$(BLUE)Generating classification metrics for agent critic Claude analyses...$(NC)"
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_claude_agents_critic_no_files.tsv data/raw/ground_truth.tsv --agent-name anthropic-critic-no-files --output output/evaluation_results/classify_claude_critic_no_files.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_claude_agents_critic_using_files_no_intro.tsv data/raw/ground_truth.tsv --agent-name anthropic-critic-no-intro --output output/evaluation_results/classify_claude_critic_no_intro.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_claude_agents_critic_using_files_with_intro.tsv data/raw/ground_truth.tsv --agent-name anthropic-critic-with-intro --output output/evaluation_results/classify_claude_critic_with_intro.csv

classify-critic-gemini: ## Generate classification metrics for agent critic Gemini analyses (3 evaluations)
	@echo "$(BLUE)Generating classification metrics for agent critic Gemini analyses...$(NC)"
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_gemini_agents_critic_no_files.tsv data/raw/ground_truth.tsv --agent-name gemini-critic-no-files --output output/evaluation_results/classify_gemini_critic_no_files.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_gemini_agents_critic_using_files_no_intro.tsv data/raw/ground_truth.tsv --agent-name gemini-critic-no-intro --output output/evaluation_results/classify_gemini_critic_no_intro.csv
	uv run python scripts/evaluate_classification_metrics.py output/analyzed_entities/analyzed_entities_gemini_agents_critic_using_files_with_intro.tsv data/raw/ground_truth.tsv --agent-name gemini-critic-with-intro --output output/evaluation_results/classify_gemini_critic_with_intro.csv

##@ Generate DSPy Models
TRAIN_FILE = output/train_test_sets/guarino_train.json
TEST_FILE = output/train_test_sets/guarino_test.json
	
generate-anthropic-%-dspy-model: ## Generate DSPy model for Claude analyses
	@echo "$(BLUE)Generating DSPy model for Claude analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model anthropic \
	--optimizer $* \
	--output output/dspy_models/guarino_claude_$*_model.json

generate-anthropic-dspy-models: \
	generate-anthropic-BootstrapFewShot-dspy-model

generate-gemini-%-dspy-model: ## Generate DSPy model for Gemini analyses
	@echo "$(BLUE)Generating DSPy model for Gemini analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model gemini \
	--optimizer $* \
	--output output/dspy_models/guarino_gemini_$*_model.json

generate-gemini-dspy-models: \
	generate-gemini-BootstrapFewShot-dspy-model \
	
generate-large-llm-dspy-models: \
	generate-anthropic-dspy-models \
	generate-gemini-dspy-models \
	generate-llama70b-dspy-models \
	generate-qwen72b-dspy-models

generate-gemma9b-%-dspy-model: ## Generate DSPy model for Gemma 9B analyses
	@echo "$(BLUE)Generating DSPy model for Gemma 9B analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model gemma9b \
	--optimizer $* \
	--output output/dspy_models/guarino_gemma9b_$*_model.json

generate-qwen7b-%-dspy-model: ## Generate DSPy model for Qwen 7B analyses
	@echo "$(BLUE)Generating DSPy model for Qwen 7B analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model qwen7b \
	--optimizer $* \
	--output output/dspy_models/guarino_qwen7b_$*_model.json

generate-llama8b-%-dspy-model: ## Generate DSPy model for LLaMA 8B analyses
	@echo "$(BLUE)Generating DSPy model for LLaMA 8B analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model llama8b \
	--optimizer $* \
	--output output/dspy_models/guarino_llama8b_$*_model.json

generate-llama3b-%-dspy-model: ## Generate DSPy model for LLaMA 3B analyses
	@echo "$(BLUE)Generating DSPy model for LLaMA 3B analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model llama3b \
	--optimizer $* \
	--output output/dspy_models/guarino_llama3b_$*_model.json

generate-gpt4o-mini-%-dspy-model: ## Generate DSPy model for GPT-4o Mini analyses
	@echo "$(BLUE)Generating DSPy model for GPT-4o Mini analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model gpt4o-mini \
	--optimizer $* \
	--output output/dspy_models/guarino_gpt4o-mini_$*_model.json

generate-gpt4o-mini-dspy-models: \
	generate-gpt4o-mini-BootstrapFewShot-dspy-model \
	
generate-llama70b-%-dspy-model: ## Generate DSPy model for LLaMA 3.3 70B analyses
	@echo "$(BLUE)Generating DSPy model for LLaMA 3.3 70B analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model llama70b \
	--optimizer $* \
	--output output/dspy_models/guarino_llama70b_$*_model.json

generate-llama70b-dspy-models: \
	generate-llama70b-BootstrapFewShot-dspy-model \
	
generate-mistral-small-%-dspy-model: ## Generate DSPy model for Mistral Small analyses
	@echo "$(BLUE)Generating DSPy model for Mistral Small analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model mistral-small-3.1 \
	--optimizer $* \
	--output output/dspy_models/guarino_mistral-small_$*_model.json

generate-mistral-small-dspy-models: \
	generate-mistral-small-BootstrapFewShot-dspy-model \

generate-mistral7b-%-dspy-model: ## Generate DSPy model for Mistral 7B analyses
	@echo "$(BLUE)Generating DSPy model for Mistral 7B analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model mistral7b \
	--optimizer $* \
	--output output/dspy_models/guarino_mistral7b_$*_model.json

generate-mistral7b-dspy-models: \
	generate-mistral7b-BootstrapFewShot-dspy-model

generate-qwen72b-%-dspy-model: ## Generate DSPy model for Qwen 2.5 72B analyses
	@echo "$(BLUE)Generating DSPy model for Qwen 2.5 72B analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model qwen72b \
	--optimizer $* \
	--output output/dspy_models/guarino_qwen72b_$*_model.json

generate-qwen72b-dspy-models: \
	generate-qwen72b-BootstrapFewShot-dspy-model \
	
generate-small-llm-dspy-models: \
	generate-gemma9b-BootstrapFewShot-dspy-model \
	generate-qwen7b-BootstrapFewShot-dspy-model \
	generate-llama8b-BootstrapFewShot-dspy-model \
	generate-llama3b-BootstrapFewShot-dspy-model \
	generate-gpt4o-mini-BootstrapFewShot-dspy-model \
	generate-mistral-small-BootstrapFewShot-dspy-model \
	generate-mistral7b-BootstrapFewShot-dspy-model
	
##@ Generate DSPy Agent Models

generate-anthropic-%-dspy-agent-model: ## Generate DSPy agent model for Claude analyses
	@echo "$(BLUE)Generating DSPy agent model for Claude analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model anthropic \
	--optimizer $* \
	--output output/dspy_models/guarino_claude_$*_agent_model.json

generate-anthropic-dspy-agent-models: \
	generate-anthropic-BootstrapFewShot-dspy-agent-model

generate-gemini-%-dspy-agent-model: ## Generate DSPy agent model for Gemini analyses
	@echo "$(BLUE)Generating DSPy agent model for Gemini analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model gemini \
	--optimizer $* \
	--output output/dspy_models/guarino_gemini_$*_agent_model.json

generate-gemini-dspy-agent-models: \
	generate-gemini-BootstrapFewShot-dspy-agent-model \
	
generate-gemma9b-%-dspy-agent-model: ## Generate DSPy agent model for Gemma 9B analyses
	@echo "$(BLUE)Generating DSPy agent model for Gemma 9B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model gemma9b \
	--optimizer $* \
	--output output/dspy_models/guarino_gemma9b_$*_agent_model.json

generate-gemma9b-dspy-agent-models: \
	generate-gemma9b-BootstrapFewShot-dspy-agent-model \
	
generate-qwen7b-%-dspy-agent-model: ## Generate DSPy agent model for Qwen 7B analyses
	@echo "$(BLUE)Generating DSPy agent model for Qwen 7B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model qwen7b \
	--optimizer $* \
	--output output/dspy_models/guarino_qwen7b_$*_agent_model.json

generate-qwen7b-dspy-agent-models: \
	generate-qwen7b-BootstrapFewShot-dspy-agent-model 
	
generate-llama8b-%-dspy-agent-model: ## Generate DSPy agent model for LLaMA 8B analyses
	@echo "$(BLUE)Generating DSPy agent model for LLaMA 8B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model llama8b \
	--optimizer $* \
	--output output/dspy_models/guarino_llama8b_$*_agent_model.json

generate-llama8b-dspy-agent-models: \
	generate-llama8b-BootstrapFewShot-dspy-agent-model 
	
generate-llama3b-%-dspy-agent-model: ## Generate DSPy agent model for LLaMA 3B analyses
	@echo "$(BLUE)Generating DSPy agent model for LLaMA 3B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model llama3b \
	--optimizer $* \
	--output output/dspy_models/guarino_llama3b_$*_agent_model.json

generate-llama3b-dspy-agent-models: \
	generate-llama3b-BootstrapFewShot-dspy-agent-model 
	
generate-gpt4o-mini-%-dspy-agent-model: ## Generate DSPy agent model for GPT-4o Mini analyses
	@echo "$(BLUE)Generating DSPy agent model for GPT-4o Mini analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model gpt4o-mini \
	--optimizer $* \
	--output output/dspy_models/guarino_gpt4o-mini_$*_agent_model.json

generate-gpt4o-mini-dspy-agent-models: \
	generate-gpt4o-mini-BootstrapFewShot-dspy-agent-model 

generate-llama70b-%-dspy-agent-model: ## Generate DSPy agent model for LLaMA 3.3 70B analyses
	@echo "$(BLUE)Generating DSPy agent model for LLaMA 3.3 70B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model llama70b \
	--optimizer $* \
	--output output/dspy_models/guarino_llama70b_$*_agent_model.json

generate-llama70b-dspy-agent-models: \
	generate-llama70b-BootstrapFewShot-dspy-agent-model 

generate-mistral-small-%-dspy-agent-model: ## Generate DSPy agent model for Mistral Small analyses
	@echo "$(BLUE)Generating DSPy agent model for Mistral Small analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model mistral-small-3.1 \
	--optimizer $* \
	--output output/dspy_models/guarino_mistral-small_$*_agent_model.json

generate-mistral-small-dspy-agent-models: \
	generate-mistral-small-BootstrapFewShot-dspy-agent-model

generate-mistral7b-%-dspy-agent-model: ## Generate DSPy agent model for Mistral 7B analyses
	@echo "$(BLUE)Generating DSPy agent model for Mistral 7B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model mistral7b \
	--optimizer $* \
	--output output/dspy_models/guarino_mistral7b_$*_agent_model.json

generate-mistral7b-dspy-agent-models: \
	generate-mistral7b-BootstrapFewShot-dspy-agent-model

generate-qwen72b-%-dspy-agent-model: ## Generate DSPy agent model for Qwen 2.5 72B analyses
	@echo "$(BLUE)Generating DSPy agent model for Qwen 2.5 72B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model qwen72b \
	--optimizer $* \
	--output output/dspy_models/guarino_qwen72b_$*_agent_model.json

generate-qwen72b-dspy-agent-models: \
	generate-qwen72b-BootstrapFewShot-dspy-agent-model 
	
generate-large-llm-dspy-agent-models: \
	generate-anthropic-dspy-agent-models \
	generate-gemini-dspy-agent-models \
	generate-llama70b-dspy-agent-models \
	generate-qwen72b-dspy-agent-models

generate-small-llm-dspy-agent-models: \
	generate-gemma9b-dspy-agent-models \
	generate-qwen7b-dspy-agent-models \
	generate-llama8b-dspy-agent-models \
	generate-llama3b-dspy-agent-models \
	generate-gpt4o-mini-dspy-agent-models \
	generate-mistral-small-dspy-agent-models \
	generate-mistral7b-dspy-agent-models

##@ DSPy Agent+Critic Model Generation

generate-anthropic-%-dspy-agent-critic-model: ## Generate DSPy agent+critic model for Claude analyses
	@echo "$(BLUE)Generating DSPy agent+critic model for Claude analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_critic_model.py $(TRAIN_FILE) $(TEST_FILE) --model anthropic \
	--optimizer $* \
	--output output/dspy_models/guarino_claude_$*_agent_critic_model.json

generate-anthropic-dspy-agent-critic-models: \
	generate-anthropic-BootstrapFewShot-dspy-agent-critic-model

generate-gemini-%-dspy-agent-critic-model: ## Generate DSPy agent+critic model for Gemini analyses
	@echo "$(BLUE)Generating DSPy agent+critic model for Gemini analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_critic_model.py $(TRAIN_FILE) $(TEST_FILE) --model gemini \
	--optimizer $* \
	--output output/dspy_models/guarino_gemini_$*_agent_critic_model.json

generate-gemini-dspy-agent-critic-models: \
	generate-gemini-BootstrapFewShot-dspy-agent-critic-model \

generate-gemma9b-%-dspy-agent-critic-model: ## Generate DSPy agent+critic model for Gemma 9B analyses
	@echo "$(BLUE)Generating DSPy agent+critic model for Gemma 9B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_critic_model.py $(TRAIN_FILE) $(TEST_FILE) --model gemma9b \
	--optimizer $* \
	--output output/dspy_models/guarino_gemma9b_$*_agent_critic_model.json

generate-gemma9b-dspy-agent-critic-models: \
	generate-gemma9b-BootstrapFewShot-dspy-agent-critic-model \

generate-qwen7b-%-dspy-agent-critic-model: ## Generate DSPy agent+critic model for Qwen 7B analyses
	@echo "$(BLUE)Generating DSPy agent+critic model for Qwen 7B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_critic_model.py $(TRAIN_FILE) $(TEST_FILE) --model qwen7b \
	--optimizer $* \
	--output output/dspy_models/guarino_qwen7b_$*_agent_critic_model.json

generate-qwen7b-dspy-agent-critic-models: \
	generate-qwen7b-BootstrapFewShot-dspy-agent-critic-model

generate-llama8b-%-dspy-agent-critic-model: ## Generate DSPy agent+critic model for LLaMA 8B analyses
	@echo "$(BLUE)Generating DSPy agent+critic model for LLaMA 8B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_critic_model.py $(TRAIN_FILE) $(TEST_FILE) --model llama8b \
	--optimizer $* \
	--output output/dspy_models/guarino_llama8b_$*_agent_critic_model.json

generate-llama8b-dspy-agent-critic-models: \
	generate-llama8b-BootstrapFewShot-dspy-agent-critic-model

generate-llama3b-%-dspy-agent-critic-model: ## Generate DSPy agent+critic model for LLaMA 3B analyses
	@echo "$(BLUE)Generating DSPy agent+critic model for LLaMA 3B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_critic_model.py $(TRAIN_FILE) $(TEST_FILE) --model llama3b \
	--optimizer $* \
	--output output/dspy_models/guarino_llama3b_$*_agent_critic_model.json

generate-llama3b-dspy-agent-critic-models: \
	generate-llama3b-BootstrapFewShot-dspy-agent-critic-model

generate-gpt4o-mini-%-dspy-agent-critic-model: ## Generate DSPy agent+critic model for GPT-4o Mini analyses
	@echo "$(BLUE)Generating DSPy agent+critic model for GPT-4o Mini analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_critic_model.py $(TRAIN_FILE) $(TEST_FILE) --model gpt4o-mini \
	--optimizer $* \
	--output output/dspy_models/guarino_gpt4o-mini_$*_agent_critic_model.json

generate-gpt4o-mini-dspy-agent-critic-models: \
	generate-gpt4o-mini-BootstrapFewShot-dspy-agent-critic-model

generate-llama70b-%-dspy-agent-critic-model: ## Generate DSPy agent+critic model for LLaMA 3.3 70B analyses
	@echo "$(BLUE)Generating DSPy agent+critic model for LLaMA 3.3 70B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_critic_model.py $(TRAIN_FILE) $(TEST_FILE) --model llama70b \
	--optimizer $* \
	--output output/dspy_models/guarino_llama70b_$*_agent_critic_model.json

generate-llama70b-dspy-agent-critic-models: \
	generate-llama70b-BootstrapFewShot-dspy-agent-critic-model

generate-mistral-small-%-dspy-agent-critic-model: ## Generate DSPy agent+critic model for Mistral Small analyses
	@echo "$(BLUE)Generating DSPy agent+critic model for Mistral Small analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_critic_model.py $(TRAIN_FILE) $(TEST_FILE) --model mistral-small-3.1 \
	--optimizer $* \
	--output output/dspy_models/guarino_mistral-small_$*_agent_critic_model.json

generate-mistral-small-dspy-agent-critic-models: \
	generate-mistral-small-BootstrapFewShot-dspy-agent-critic-model

generate-mistral7b-%-dspy-agent-critic-model: ## Generate DSPy agent+critic model for Mistral 7B analyses
	@echo "$(BLUE)Generating DSPy agent+critic model for Mistral 7B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_critic_model.py $(TRAIN_FILE) $(TEST_FILE) --model mistral7b \
	--optimizer $* \
	--output output/dspy_models/guarino_mistral7b_$*_agent_critic_model.json

generate-mistral7b-dspy-agent-critic-models: \
	generate-mistral7b-BootstrapFewShot-dspy-agent-critic-model

generate-qwen72b-%-dspy-agent-critic-model: ## Generate DSPy agent+critic model for Qwen 2.5 72B analyses
	@echo "$(BLUE)Generating DSPy agent+critic model for Qwen 2.5 72B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_critic_model.py $(TRAIN_FILE) $(TEST_FILE) --model qwen72b \
	--optimizer $* \
	--output output/dspy_models/guarino_qwen72b_$*_agent_critic_model.json

generate-qwen72b-dspy-agent-critic-models: \
	generate-qwen72b-BootstrapFewShot-dspy-agent-critic-model

generate-large-llm-dspy-agent-critic-models: \
	generate-anthropic-dspy-agent-critic-models \
	generate-gemini-dspy-agent-critic-models \
	generate-llama70b-dspy-agent-critic-models \
	generate-qwen72b-dspy-agent-critic-models

generate-small-llm-dspy-agent-critic-models: \
	generate-gemma9b-dspy-agent-critic-models \
	generate-qwen7b-dspy-agent-critic-models \
	generate-llama8b-dspy-agent-critic-models \
	generate-llama3b-dspy-agent-critic-models \
	generate-gpt4o-mini-dspy-agent-critic-models \
	generate-mistral-small-dspy-agent-critic-models \
	generate-mistral7b-dspy-agent-critic-models

##@ Batch Analysis Non-Agent DSPy Compiled Models
ONTOLOGY_FILE = output/ontologies/guarino_messy.owl
MODEL_DIR = output/dspy_models
ANALYZED_OUTPUT_DIR = output/analyzed_entities
EVALUATION_RESULTS_DIR = output/evaluation_results

# The function $(shell echo $@ | sed 's/.*BootstrapFewShot-//') is used to extract the model name from the target name. 
# E.g., If the target is batch-agent-dspy-anthropic-BootstrapFewShot-gemma9b, the function will return "gemma9b".
define batch-non-agent-dspy
	@echo "DSPy Batch Analyzing guarino_$(1)_$(2)_model.json using model $(3)"

	uv run python scripts/batch_analyze_dspy.py $(ONTOLOGY_FILE) \
	--compiled-model $(MODEL_DIR)/guarino_$(1)_$(2)_model.json \
	--model $(3) \
	--output $(ANALYZED_OUTPUT_DIR)/dspy_analyzed_entities_$(1)_$(2)_$(3).tsv \
	&& \
	uv run python scripts/evaluate_classification_metrics.py\
		$(strip \
			$(ANALYZED_OUTPUT_DIR)/dspy_analyzed_entities_$(1)_$(2)_$(3).tsv \
			data/raw/ground_truth.tsv
		) \
	--agent-name $(3) \
	--output $(EVALUATION_RESULTS_DIR)/classify_dspy_$(1)_$(2)_$(shell echo $@ | sed 's/.*BootstrapFewShot-//').csv
endef

batch-non-agent-dspy-anthropic-%-gemma9b:
	$(call batch-non-agent-dspy,claude,$*,dspy_claude_gemma9b)

batch-non-agent-dspy-anthropic-%-qwen7b:
	$(call batch-non-agent-dspy,claude,$*,dspy_claude_qwen7b)

batch-non-agent-dspy-anthropic-%-llama8b:
	$(call batch-non-agent-dspy,claude,$*,dspy_claude_llama8b)

batch-non-agent-dspy-anthropic-%-llama3b:
	$(call batch-non-agent-dspy,claude,$*,dspy_claude_llama3b)

batch-non-agent-dspy-gemini-%-gemma9b:
	$(call batch-non-agent-dspy,gemini,$*,dspy_gemini_gemma9b)

batch-non-agent-dspy-gemini-%-qwen7b:
	$(call batch-non-agent-dspy,gemini,$*,dspy_gemini_qwen7b)

batch-non-agent-dspy-gemini-%-llama8b:
	$(call batch-non-agent-dspy,gemini,$*,dspy_gemini_llama8b)

batch-non-agent-dspy-gemini-%-llama3b:
	$(call batch-non-agent-dspy,gemini,$*,dspy_gemini_llama3b)

batch-non-agent-dspy-anthropic-%-gpt4o-mini:
	$(call batch-non-agent-dspy,claude,$*,dspy_claude_gpt4o-mini)

batch-non-agent-dspy-anthropic-%-mistral-small-3.1:
	$(call batch-non-agent-dspy,claude,$*,dspy_claude_mistral-small-3.1)

batch-non-agent-dspy-anthropic-%-mistral7b:
	$(call batch-non-agent-dspy,claude,$*,dspy_claude_mistral7b)

batch-non-agent-dspy-anthropic-%-llama70b:
	$(call batch-non-agent-dspy,claude,$*,dspy_claude_llama70b)

batch-non-agent-dspy-anthropic-%-qwen72b:
	$(call batch-non-agent-dspy,claude,$*,dspy_claude_qwen72b)

batch-non-agent-dspy-gemini-%-gpt4o-mini:
	$(call batch-non-agent-dspy,gemini,$*,dspy_gemini_gpt4o-mini)

batch-non-agent-dspy-gemini-%-mistral-small-3.1:
	$(call batch-non-agent-dspy,gemini,$*,dspy_gemini_mistral-small-3.1)

batch-non-agent-dspy-gemini-%-mistral7b:
	$(call batch-non-agent-dspy,gemini,$*,dspy_gemini_mistral7b)

batch-non-agent-dspy-gemini-%-llama70b:
	$(call batch-non-agent-dspy,gemini,$*,dspy_gemini_llama70b)

batch-non-agent-dspy-gemini-%-qwen72b:
	$(call batch-non-agent-dspy,gemini,$*,dspy_gemini_qwen72b)

batch-non-agent-dspy-anthropic-small-models: \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-gemma9b \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-qwen7b \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-llama8b \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-llama3b \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-gpt4o-mini \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-mistral-small-3.1 \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-mistral7b \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-llama70b \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-qwen72b

batch-non-agent-dspy-gemini-small-models: \
	batch-non-agent-dspy-gemini-BootstrapFewShot-gemma9b \
	batch-non-agent-dspy-gemini-BootstrapFewShot-qwen7b \
	batch-non-agent-dspy-gemini-BootstrapFewShot-llama8b \
	batch-non-agent-dspy-gemini-BootstrapFewShot-llama3b \
	batch-non-agent-dspy-gemini-BootstrapFewShot-gpt4o-mini \
	batch-non-agent-dspy-gemini-BootstrapFewShot-mistral-small-3.1 \
	batch-non-agent-dspy-gemini-BootstrapFewShot-mistral7b \
	batch-non-agent-dspy-gemini-BootstrapFewShot-llama70b \
	batch-non-agent-dspy-gemini-BootstrapFewShot-qwen72b

batch-non-agent-dspy-small-models: \
	batch-non-agent-dspy-anthropic-small-models \
	batch-non-agent-dspy-gemini-small-models

##@ Batch Analysis Agent DSPy Compiled Models

# The function $(shell echo $@ | sed 's/.*BootstrapFewShot-//') is used to extract the model name from the target name. 
# E.g., If the target is batch-agent-dspy-anthropic-BootstrapFewShot-gemma9b, the function will return "gemma9b".
define batch-agent-dspy
	@echo "DSPy Agent Batch Analyzing guarino_$(1)_$(2)_agent_model.json using model $(3)"

	uv run python scripts/batch_analyze_agent_dspy.py $(ONTOLOGY_FILE) \
	--compiled-model $(MODEL_DIR)/guarino_$(1)_$(2)_agent_model.json \
	--model $(3) \
	--output $(ANALYZED_OUTPUT_DIR)/dspy_agent_analyzed_entities_$(1)_$(2)_$(3).tsv \
	&& \
	uv run python scripts/evaluate_classification_metrics.py\
		$(strip \
			$(ANALYZED_OUTPUT_DIR)/dspy_agent_analyzed_entities_$(1)_$(2)_$(3).tsv \
			data/raw/ground_truth.tsv
		) \
	--agent-name $(3) \
	--output $(EVALUATION_RESULTS_DIR)/classify_dspy_agent_$(1)_$(2)_$(shell echo $@ | sed 's/.*BootstrapFewShot-//').csv
endef

batch-agent-dspy-anthropic-%-gemma9b:
	$(call batch-agent-dspy,claude,$*,dspy_agent_claude_gemma9b)

batch-agent-dspy-anthropic-%-qwen7b:
	$(call batch-agent-dspy,claude,$*,dspy_agent_claude_qwen7b)

batch-agent-dspy-anthropic-%-llama8b:
	$(call batch-agent-dspy,claude,$*,dspy_agent_claude_llama8b)

batch-agent-dspy-anthropic-%-llama3b:
	$(call batch-agent-dspy,claude,$*,dspy_agent_claude_llama3b)

batch-agent-dspy-gemini-%-gemma9b:
	$(call batch-agent-dspy,gemini,$*,dspy_agent_gemini_gemma9b)

batch-agent-dspy-gemini-%-qwen7b:
	$(call batch-agent-dspy,gemini,$*,dspy_agent_gemini_qwen7b)

batch-agent-dspy-gemini-%-llama8b:
	$(call batch-agent-dspy,gemini,$*,dspy_agent_gemini_llama8b)

batch-agent-dspy-gemini-%-llama3b:
	$(call batch-agent-dspy,gemini,$*,dspy_agent_gemini_llama3b)

batch-agent-dspy-anthropic-%-gpt4o-mini:
	$(call batch-agent-dspy,claude,$*,dspy_agent_claude_gpt4o-mini)

batch-agent-dspy-anthropic-%-mistral-small-3.1:
	$(call batch-agent-dspy,claude,$*,dspy_agent_claude_mistral-small-3.1)

batch-agent-dspy-anthropic-%-mistral7b:
	$(call batch-agent-dspy,claude,$*,dspy_agent_claude_mistral7b)

batch-agent-dspy-anthropic-%-llama70b:
	$(call batch-agent-dspy,claude,$*,dspy_agent_claude_llama70b)

batch-agent-dspy-anthropic-%-qwen72b:
	$(call batch-agent-dspy,claude,$*,dspy_agent_claude_qwen72b)

batch-agent-dspy-gemini-%-gpt4o-mini:
	$(call batch-agent-dspy,gemini,$*,dspy_agent_gemini_gpt4o-mini)

batch-agent-dspy-gemini-%-mistral-small-3.1:
	$(call batch-agent-dspy,gemini,$*,dspy_agent_gemini_mistral-small-3.1)

batch-agent-dspy-gemini-%-mistral7b:
	$(call batch-agent-dspy,gemini,$*,dspy_agent_gemini_mistral7b)

batch-agent-dspy-gemini-%-llama70b:
	$(call batch-agent-dspy,gemini,$*,dspy_agent_gemini_llama70b)

batch-agent-dspy-gemini-%-qwen72b:
	$(call batch-agent-dspy,gemini,$*,dspy_agent_gemini_qwen72b)

batch-agent-dspy-anthropic-small-models: \
	batch-agent-dspy-anthropic-BootstrapFewShot-gemma9b \
	batch-agent-dspy-anthropic-BootstrapFewShot-qwen7b \
	batch-agent-dspy-anthropic-BootstrapFewShot-llama8b \
	batch-agent-dspy-anthropic-BootstrapFewShot-llama3b \
	batch-agent-dspy-anthropic-BootstrapFewShot-gpt4o-mini \
	batch-agent-dspy-anthropic-BootstrapFewShot-mistral-small-3.1 \
	batch-agent-dspy-anthropic-BootstrapFewShot-mistral7b \
	batch-agent-dspy-anthropic-BootstrapFewShot-llama70b \
	batch-agent-dspy-anthropic-BootstrapFewShot-qwen72b

batch-agent-dspy-gemini-small-models: \
	batch-agent-dspy-gemini-BootstrapFewShot-gemma9b \
	batch-agent-dspy-gemini-BootstrapFewShot-qwen7b \
	batch-agent-dspy-gemini-BootstrapFewShot-llama8b \
	batch-agent-dspy-gemini-BootstrapFewShot-llama3b \
	batch-agent-dspy-gemini-BootstrapFewShot-gpt4o-mini \
	batch-agent-dspy-gemini-BootstrapFewShot-mistral-small-3.1 \
	batch-agent-dspy-gemini-BootstrapFewShot-mistral7b \
	batch-agent-dspy-gemini-BootstrapFewShot-llama70b \
	batch-agent-dspy-gemini-BootstrapFewShot-qwen72b

batch-agent-dspy-small-models: \
	batch-agent-dspy-anthropic-small-models \
	batch-agent-dspy-gemini-small-models

##@ Batch Analysis Agent+Critic DSPy Compiled Models

# The function $(shell echo $@ | sed 's/.*BootstrapFewShot-//') is used to extract the model name from the target name. 
# E.g., If the target is batch-agent-dspy-anthropic-BootstrapFewShot-gemma9b, the function will return "gemma9b".
define batch-agent-critic-dspy
	@echo "DSPy Agent+Critic Batch Analyzing guarino_$(1)_$(2)_agent_critic_model.json using model $(3)"

	uv run python scripts/batch_analyze_agent_critic_dspy.py $(ONTOLOGY_FILE) \
	--compiled-model $(MODEL_DIR)/guarino_$(1)_$(2)_agent_critic_model.json \
	--model $(3) \
	--output $(ANALYZED_OUTPUT_DIR)/dspy_agent_critic_analyzed_entities_$(1)_$(2)_$(3).tsv \
	&& \
	uv run python scripts/evaluate_classification_metrics.py\
		$(strip \
			$(ANALYZED_OUTPUT_DIR)/dspy_agent_critic_analyzed_entities_$(1)_$(2)_$(3).tsv \
			data/raw/ground_truth.tsv
		) \
	--agent-name $(3) \
	--output $(EVALUATION_RESULTS_DIR)/classify_dspy_agent_critic_$(1)_$(2)_$(shell echo $@ | sed 's/.*BootstrapFewShot-//').csv
endef

batch-agent-critic-dspy-anthropic-%-gemma9b:
	$(call batch-agent-critic-dspy,claude,$*,dspy_agent_critic_claude_gemma9b)

batch-agent-critic-dspy-anthropic-%-qwen7b:
	$(call batch-agent-critic-dspy,claude,$*,dspy_agent_critic_claude_qwen7b)

batch-agent-critic-dspy-anthropic-%-llama8b:
	$(call batch-agent-critic-dspy,claude,$*,dspy_agent_critic_claude_llama8b)

batch-agent-critic-dspy-anthropic-%-llama3b:
	$(call batch-agent-critic-dspy,claude,$*,dspy_agent_critic_claude_llama3b)

batch-agent-critic-dspy-gemini-%-gemma9b:
	$(call batch-agent-critic-dspy,gemini,$*,dspy_agent_critic_gemini_gemma9b)

batch-agent-critic-dspy-gemini-%-qwen7b:
	$(call batch-agent-critic-dspy,gemini,$*,dspy_agent_critic_gemini_qwen7b)

batch-agent-critic-dspy-gemini-%-llama8b:
	$(call batch-agent-critic-dspy,gemini,$*,dspy_agent_critic_gemini_llama8b)

batch-agent-critic-dspy-gemini-%-llama3b:
	$(call batch-agent-critic-dspy,gemini,$*,dspy_agent_critic_gemini_llama3b)

batch-agent-critic-dspy-anthropic-%-gpt4o-mini:
	$(call batch-agent-critic-dspy,claude,$*,dspy_agent_critic_claude_gpt4o-mini)

batch-agent-critic-dspy-anthropic-%-mistral-small-3.1:
	$(call batch-agent-critic-dspy,claude,$*,dspy_agent_critic_claude_mistral-small-3.1)

batch-agent-critic-dspy-anthropic-%-mistral7b:
	$(call batch-agent-critic-dspy,claude,$*,dspy_agent_critic_claude_mistral7b)

batch-agent-critic-dspy-anthropic-%-llama70b:
	$(call batch-agent-critic-dspy,claude,$*,dspy_agent_critic_claude_llama70b)

batch-agent-critic-dspy-anthropic-%-qwen72b:
	$(call batch-agent-critic-dspy,claude,$*,dspy_agent_critic_claude_qwen72b)

batch-agent-critic-dspy-gemini-%-gpt4o-mini:
	$(call batch-agent-critic-dspy,gemini,$*,dspy_agent_critic_gemini_gpt4o-mini)

batch-agent-critic-dspy-gemini-%-mistral-small-3.1:
	$(call batch-agent-critic-dspy,gemini,$*,dspy_agent_critic_gemini_mistral-small-3.1)

batch-agent-critic-dspy-gemini-%-mistral7b:
	$(call batch-agent-critic-dspy,gemini,$*,dspy_agent_critic_gemini_mistral7b)

batch-agent-critic-dspy-gemini-%-llama70b:
	$(call batch-agent-critic-dspy,gemini,$*,dspy_agent_critic_gemini_llama70b)

batch-agent-critic-dspy-gemini-%-qwen72b:
	$(call batch-agent-critic-dspy,gemini,$*,dspy_agent_critic_gemini_qwen72b)

batch-agent-critic-dspy-anthropic-small-models: \
	batch-agent-critic-dspy-anthropic-BootstrapFewShot-gemma9b \
	batch-agent-critic-dspy-anthropic-BootstrapFewShot-qwen7b \
	batch-agent-critic-dspy-anthropic-BootstrapFewShot-llama8b \
	batch-agent-critic-dspy-anthropic-BootstrapFewShot-llama3b \
	batch-agent-critic-dspy-anthropic-BootstrapFewShot-gpt4o-mini \
	batch-agent-critic-dspy-anthropic-BootstrapFewShot-mistral-small-3.1 \
	batch-agent-critic-dspy-anthropic-BootstrapFewShot-mistral7b \
	batch-agent-critic-dspy-anthropic-BootstrapFewShot-llama70b \
	batch-agent-critic-dspy-anthropic-BootstrapFewShot-qwen72b

batch-agent-critic-dspy-gemini-small-models: \
	batch-agent-critic-dspy-gemini-BootstrapFewShot-gemma9b \
	batch-agent-critic-dspy-gemini-BootstrapFewShot-qwen7b \
	batch-agent-critic-dspy-gemini-BootstrapFewShot-llama8b \
	batch-agent-critic-dspy-gemini-BootstrapFewShot-llama3b \
	batch-agent-critic-dspy-gemini-BootstrapFewShot-gpt4o-mini \
	batch-agent-critic-dspy-gemini-BootstrapFewShot-mistral-small-3.1 \
	batch-agent-critic-dspy-gemini-BootstrapFewShot-mistral7b \
	batch-agent-critic-dspy-gemini-BootstrapFewShot-llama70b \
	batch-agent-critic-dspy-gemini-BootstrapFewShot-qwen72b

batch-agent-critic-dspy-small-models: \
	batch-agent-critic-dspy-anthropic-small-models \
	batch-agent-critic-dspy-gemini-small-models

##@ Results Collection and Reports

collect-non-agent: ## Collect non-agent evaluation results into reports
	@echo "$(BLUE)Collecting non-agent results...$(NC)"
	uv run python scripts/collect_evaluations.py \
		--files output/evaluation_results/evaluate_claude_no_files.json \
				output/evaluation_results/evaluate_claude_pdf.json \
				output/evaluation_results/evaluate_claude_text.json \
				output/evaluation_results/evaluate_claude_corrected_text.json \
				output/evaluation_results/evaluate_gemini_no_files.json \
				output/evaluation_results/evaluate_gemini_pdf.json \
				output/evaluation_results/evaluate_gemini_text.json \
				output/evaluation_results/evaluate_gemini_corrected_text.json \
		--indexes no-files pdf text corrected no-files pdf text corrected \
		--output output/collect_non_agent_results.tsv
	uv run python scripts/collect_evaluations.py \
		--files output/evaluation_results/evaluate_claude_no_files.json \
				output/evaluation_results/evaluate_claude_pdf.json \
				output/evaluation_results/evaluate_claude_text.json \
				output/evaluation_results/evaluate_claude_corrected_text.json \
				output/evaluation_results/evaluate_gemini_no_files.json \
				output/evaluation_results/evaluate_gemini_pdf.json \
				output/evaluation_results/evaluate_gemini_text.json \
				output/evaluation_results/evaluate_gemini_corrected_text.json \
		--indexes no-files pdf text corrected no-files pdf text corrected \
		--output output/collect_non_agent_results.md
	cp output/collect_non_agent_results.md docs/reports/NON_AGENT_BATCH_ANALYSIS_REPORT.md

collect-agent: ## Collect agent evaluation results into reports
	@echo "$(BLUE)Collecting agent results...$(NC)"
	uv run python scripts/collect_evaluations.py \
		--files output/evaluation_results/evaluate_claude_agents_no_files.json \
				output/evaluation_results/evaluate_claude_agents_using_files_no_intro.json \
				output/evaluation_results/evaluate_claude_agents_using_files_with_intro.json \
				output/evaluation_results/evaluate_gemini_agents_no_files.json \
				output/evaluation_results/evaluate_gemini_agents_using_files_no_intro.json \
				output/evaluation_results/evaluate_gemini_agents_using_files_with_intro.json \
		--indexes no-files no-intro with-intro no-files no-intro with-intro \
		--output output/collect_agent_results.tsv
	uv run python scripts/collect_evaluations.py \
		--files output/evaluation_results/evaluate_claude_agents_no_files.json \
				output/evaluation_results/evaluate_claude_agents_using_files_no_intro.json \
				output/evaluation_results/evaluate_claude_agents_using_files_with_intro.json \
				output/evaluation_results/evaluate_gemini_agents_no_files.json \
				output/evaluation_results/evaluate_gemini_agents_using_files_no_intro.json \
				output/evaluation_results/evaluate_gemini_agents_using_files_with_intro.json \
		--indexes no-files no-intro with-intro no-files no-intro with-intro \
		--output output/collect_agent_results.md
	cp output/collect_agent_results.md docs/reports/AGENT_BATCH_ANALYSIS_REPORT.md

collect-critic: ## Collect agent critic evaluation results into reports
	@echo "$(BLUE)Collecting agent critic results...$(NC)"
	uv run python scripts/collect_evaluations.py \
		--files output/evaluation_results/evaluate_claude_agents_critic_no_files.json \
				output/evaluation_results/evaluate_claude_agents_critic_using_files_no_intro.json \
				output/evaluation_results/evaluate_claude_agents_critic_using_files_with_intro.json \
				output/evaluation_results/evaluate_gemini_agents_critic_no_files.json \
				output/evaluation_results/evaluate_gemini_agents_critic_using_files_no_intro.json \
				output/evaluation_results/evaluate_gemini_agents_critic_using_files_with_intro.json \
		--indexes no-files no-intro with-intro no-files no-intro with-intro \
		--output output/collect_agent_critic_results.tsv
	uv run python scripts/collect_evaluations.py \
		--files output/evaluation_results/evaluate_claude_agents_critic_no_files.json \
				output/evaluation_results/evaluate_claude_agents_critic_using_files_no_intro.json \
				output/evaluation_results/evaluate_claude_agents_critic_using_files_with_intro.json \
				output/evaluation_results/evaluate_gemini_agents_critic_no_files.json \
				output/evaluation_results/evaluate_gemini_agents_critic_using_files_no_intro.json \
				output/evaluation_results/evaluate_gemini_agents_critic_using_files_with_intro.json \
		--indexes no-files no-intro with-intro no-files no-intro with-intro \
		--output output/collect_agent_critic_results.md
	cp output/collect_agent_critic_results.md docs/reports/AGENT_CRITIC_BATCH_ANALYSIS_REPORT.md

batch-non-agent-expanded: ## Run expanded non-agent batch analysis (13 models x 2 configs)
	@echo "$(BLUE)Running expanded non-agent batch analysis...$(NC)"
	chmod +x scripts/reproduce_expanded_non_agent.sh
	./scripts/reproduce_expanded_non_agent.sh

reports: collect-non-agent collect-agent collect-critic batch-non-agent-expanded ## Generate all analysis reports

##@ Local Fine-Tuning (Apple Silicon / macOS)

FINETUNE_DATA = output/fine-tunning/data/finetune_data.jsonl
FINETUNE_MODELS_DIR = output/fine-tunning/models
FINETUNE_ADAPTERS_DIR = output/fine-tunning/adapters

finetune-mistral7b: ## Fine-tune Mistral-7B-Instruct-v0.3 locally (mistral7b)
	@echo "$(BLUE)Fine-tuning Mistral 7B locally...$(NC)"
	uv run python scripts/finetune_local.py \
		--hf-model mistralai/Mistral-7B-Instruct-v0.3 \
		--mlx-path $(FINETUNE_MODELS_DIR)/mistral-7b-mlx \
		--data $(FINETUNE_DATA) \
		--adapter $(FINETUNE_ADAPTERS_DIR)/mistral7b-ontoclean \
		--fused $(FINETUNE_MODELS_DIR)/mistral7b-ontoclean-fused \
		--gguf $(FINETUNE_MODELS_DIR)/mistral7b-ontoclean.gguf \
		--ollama-name mistral7b-ontoclean

finetune-gemma9b: ## Fine-tune Gemma-2-9B-IT locally (gemma9b) — requires HF token + license agreement
	@echo "$(BLUE)Fine-tuning Gemma 9B locally...$(NC)"
	uv run python scripts/finetune_local.py \
		--hf-model google/gemma-2-9b-it \
		--mlx-path $(FINETUNE_MODELS_DIR)/gemma-9b-mlx \
		--data $(FINETUNE_DATA) \
		--adapter $(FINETUNE_ADAPTERS_DIR)/gemma9b-ontoclean \
		--fused $(FINETUNE_MODELS_DIR)/gemma9b-ontoclean-fused \
		--gguf $(FINETUNE_MODELS_DIR)/gemma9b-ontoclean.gguf \
		--ollama-name gemma9b-ontoclean \
		--no-system-role

finetune-qwen7b: ## Fine-tune Qwen2.5-7B-Instruct locally (qwen7b)
	@echo "$(BLUE)Fine-tuning Qwen 7B locally...$(NC)"
	uv run python scripts/finetune_local.py \
		--hf-model Qwen/Qwen2.5-7B-Instruct \
		--mlx-path $(FINETUNE_MODELS_DIR)/qwen2.5-7b-mlx \
		--data $(FINETUNE_DATA) \
		--adapter $(FINETUNE_ADAPTERS_DIR)/qwen7b-ontoclean \
		--fused $(FINETUNE_MODELS_DIR)/qwen7b-ontoclean-fused \
		--gguf $(FINETUNE_MODELS_DIR)/qwen7b-ontoclean.gguf \
		--ollama-name qwen7b-ontoclean

finetune-llama8b: ## Fine-tune Llama-3.1-8B-Instruct locally (llama8b)
	@echo "$(BLUE)Fine-tuning Llama 8B locally...$(NC)"
	uv run python scripts/finetune_local.py \
		--hf-model meta-llama/Llama-3.1-8B-Instruct \
		--mlx-path $(FINETUNE_MODELS_DIR)/llama-8b-mlx \
		--data $(FINETUNE_DATA) \
		--adapter $(FINETUNE_ADAPTERS_DIR)/llama8b-ontoclean \
		--fused $(FINETUNE_MODELS_DIR)/llama8b-ontoclean-fused \
		--gguf $(FINETUNE_MODELS_DIR)/llama8b-ontoclean.gguf \
		--ollama-name llama8b-ontoclean

finetune-llama3b: ## Fine-tune Llama-3.2-3B-Instruct locally (llama3b)
	@echo "$(BLUE)Fine-tuning Llama 3B locally...$(NC)"
	uv run python scripts/finetune_local.py \
		--hf-model meta-llama/Llama-3.2-3B-Instruct \
		--mlx-path $(FINETUNE_MODELS_DIR)/llama-3b-mlx \
		--data $(FINETUNE_DATA) \
		--adapter $(FINETUNE_ADAPTERS_DIR)/llama3b-ontoclean \
		--fused $(FINETUNE_MODELS_DIR)/llama3b-ontoclean-fused \
		--gguf $(FINETUNE_MODELS_DIR)/llama3b-ontoclean.gguf \
		--ollama-name llama3b-ontoclean

finetune-all-local: finetune-mistral7b finetune-gemma9b finetune-qwen7b finetune-llama8b finetune-llama3b ## Fine-tune all five small models locally

TEST_OUTPUT_DIR = output/finetuned_tests

# All test targets use mlx_lm.server (via test_with_mlx_server.py) to bypass
# the Ollama GGUF crash: mlx_lm's convert_to_gguf writes 'llama' architecture
# metadata for all models, causing Ollama to crash on non-LLaMA architectures
# and on some LLaMA models too. Serving the fused safetensors directly avoids
# the GGUF step entirely.

test-finetuned-mistral7b: ## Test mistral7b-ontoclean via mlx_lm.server
	@echo "$(BLUE)Testing mistral7b-ontoclean...$(NC)"
	uv run python scripts/test_with_mlx_server.py \
		--model-path $(FINETUNE_MODELS_DIR)/mistral7b-ontoclean-fused \
		--model-name mistral7b-ontoclean \
		--output $(TEST_OUTPUT_DIR)/mistral7b_ontoclean_results.tsv

test-finetuned-gemma9b: ## Test gemma9b-ontoclean via mlx_lm.server
	@echo "$(BLUE)Testing gemma9b-ontoclean...$(NC)"
	uv run python scripts/test_with_mlx_server.py \
		--model-path $(FINETUNE_MODELS_DIR)/gemma9b-ontoclean-fused \
		--model-name gemma9b-ontoclean \
		--no-system-role \
		--output $(TEST_OUTPUT_DIR)/gemma9b_ontoclean_results.tsv

test-finetuned-qwen7b: ## Test qwen7b-ontoclean via mlx_lm.server
	@echo "$(BLUE)Testing qwen7b-ontoclean...$(NC)"
	uv run python scripts/test_with_mlx_server.py \
		--model-path $(FINETUNE_MODELS_DIR)/qwen7b-ontoclean-fused \
		--model-name qwen7b-ontoclean \
		--output $(TEST_OUTPUT_DIR)/qwen7b_ontoclean_results.tsv

test-finetuned-llama8b: ## Test llama8b-ontoclean via mlx_lm.server
	@echo "$(BLUE)Testing llama8b-ontoclean...$(NC)"
	uv run python scripts/test_with_mlx_server.py \
		--model-path $(FINETUNE_MODELS_DIR)/llama8b-ontoclean-fused \
		--model-name llama8b-ontoclean \
		--output $(TEST_OUTPUT_DIR)/llama8b_ontoclean_results.tsv

test-finetuned-llama3b: ## Test llama3b-ontoclean via mlx_lm.server
	@echo "$(BLUE)Testing llama3b-ontoclean...$(NC)"
	uv run python scripts/test_with_mlx_server.py \
		--model-path $(FINETUNE_MODELS_DIR)/llama3b-ontoclean-fused \
		--model-name llama3b-ontoclean \
		--output $(TEST_OUTPUT_DIR)/llama3b_ontoclean_results.tsv

test-finetuned-all: test-finetuned-mistral7b test-finetuned-gemma9b test-finetuned-qwen7b test-finetuned-llama8b test-finetuned-llama3b ## Test all five fine-tuned models

##@ Complete Workflows

reproduce-batch: batch-non-agent eval-non-agent classify-non-agent collect-non-agent batch-agent eval-agent classify-agent collect-agent batch-critic eval-critic classify-critic collect-critic batch-non-agent-expanded ## Run complete batch analysis reproduction with classification metrics (46 experiments + 20 classification evaluations)
	@echo "$(GREEN)Complete batch analysis reproduction finished!$(NC)"
	@echo "Reports available in docs/reports/"
	@echo "Classification metrics available in output/evaluation_results/classify_*.csv"
