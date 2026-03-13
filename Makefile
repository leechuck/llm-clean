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
        generate-mistral-small-dspy-models generate-qwen72b-dspy-models \
        generate-anthropic-dspy-agent-models generate-gemini-dspy-agent-models \
        generate-gemma9b-dspy-agent-models generate-qwen7b-dspy-agent-models \
        generate-llama8b-dspy-agent-models generate-llama3b-dspy-agent-models \
        generate-gpt4o-mini-dspy-agent-models generate-llama70b-dspy-agent-models \
        generate-mistral-small-dspy-agent-models generate-qwen72b-dspy-agent-models \
        generate-large-llm-dspy-agent-models generate-small-llm-dspy-agent-models

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
	generate-anthropic-BootstrapFewShot-dspy-model \
	generate-anthropic-BootstrapFewShotWithRandomSearch-dspy-model \
	generate-anthropic-COPRO-dspy-model \
	generate-anthropic-MIPROv2-dspy-model

generate-gemini-%-dspy-model: ## Generate DSPy model for Gemini analyses
	@echo "$(BLUE)Generating DSPy model for Gemini analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model gemini \
	--optimizer $* \
	--output output/dspy_models/guarino_gemini_$*_model.json

generate-gemini-dspy-models: \
	generate-gemini-BootstrapFewShot-dspy-model \
	generate-gemini-BootstrapFewShotWithRandomSearch-dspy-model \
	generate-gemini-COPRO-dspy-model \
	generate-gemini-MIPROv2-dspy-model

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
	generate-gpt4o-mini-BootstrapFewShotWithRandomSearch-dspy-model \
	generate-gpt4o-mini-COPRO-dspy-model \
	generate-gpt4o-mini-MIPROv2-dspy-model

generate-llama70b-%-dspy-model: ## Generate DSPy model for LLaMA 3.3 70B analyses
	@echo "$(BLUE)Generating DSPy model for LLaMA 3.3 70B analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model llama70b \
	--optimizer $* \
	--output output/dspy_models/guarino_llama70b_$*_model.json

generate-llama70b-dspy-models: \
	generate-llama70b-BootstrapFewShot-dspy-model \
	generate-llama70b-BootstrapFewShotWithRandomSearch-dspy-model \
	generate-llama70b-COPRO-dspy-model \
	generate-llama70b-MIPROv2-dspy-model

generate-mistral-small-%-dspy-model: ## Generate DSPy model for Mistral Small analyses
	@echo "$(BLUE)Generating DSPy model for Mistral Small analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model mistral-small-3.1 \
	--optimizer $* \
	--output output/dspy_models/guarino_mistral-small_$*_model.json

generate-mistral-small-dspy-models: \
	generate-mistral-small-BootstrapFewShot-dspy-model \
	generate-mistral-small-BootstrapFewShotWithRandomSearch-dspy-model \
	generate-mistral-small-COPRO-dspy-model \
	generate-mistral-small-MIPROv2-dspy-model

generate-qwen72b-%-dspy-model: ## Generate DSPy model for Qwen 2.5 72B analyses
	@echo "$(BLUE)Generating DSPy model for Qwen 2.5 72B analyses...$(NC)"
	uv run python scripts/generate_dspy_model.py $(TRAIN_FILE) $(TEST_FILE) --model qwen72b \
	--optimizer $* \
	--output output/dspy_models/guarino_qwen72b_$*_model.json

generate-qwen72b-dspy-models: \
	generate-qwen72b-BootstrapFewShot-dspy-model \
	generate-qwen72b-BootstrapFewShotWithRandomSearch-dspy-model \
	generate-qwen72b-COPRO-dspy-model \
	generate-qwen72b-MIPROv2-dspy-model

generate-small-llm-dspy-models: \
	generate-gemma9b-BootstrapFewShot-dspy-model \
	generate-gemma9b-BootstrapFewShotWithRandomSearch-dspy-model \
	generate-gemma9b-COPRO-dspy-model \
	generate-gemma9b-MIPROv2-dspy-model \
	generate-qwen7b-BootstrapFewShot-dspy-model \
	generate-qwen7b-BootstrapFewShotWithRandomSearch-dspy-model \
	generate-qwen7b-COPRO-dspy-model \
	generate-qwen7b-MIPROv2-dspy-model \
	generate-llama8b-BootstrapFewShot-dspy-model \
	generate-llama8b-BootstrapFewShotWithRandomSearch-dspy-model \
	generate-llama8b-COPRO-dspy-model \
	generate-llama8b-MIPROv2-dspy-model \
	generate-llama3b-BootstrapFewShot-dspy-model \
	generate-llama3b-BootstrapFewShotWithRandomSearch-dspy-model \
	generate-llama3b-COPRO-dspy-model \
	generate-llama3b-MIPROv2-dspy-model \
	generate-gpt4o-mini-BootstrapFewShot-dspy-model \
	generate-gpt4o-mini-BootstrapFewShotWithRandomSearch-dspy-model \
	generate-gpt4o-mini-COPRO-dspy-model \
	generate-gpt4o-mini-MIPROv2-dspy-model \
	generate-mistral-small-BootstrapFewShot-dspy-model \
	generate-mistral-small-BootstrapFewShotWithRandomSearch-dspy-model \
	generate-mistral-small-COPRO-dspy-model \
	generate-mistral-small-MIPROv2-dspy-model

##@ Generate DSPy Agent Models

generate-anthropic-%-dspy-agent-model: ## Generate DSPy agent model for Claude analyses
	@echo "$(BLUE)Generating DSPy agent model for Claude analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model anthropic \
	--optimizer $* \
	--output output/dspy_models/guarino_claude_$*_agent_model.json

generate-anthropic-dspy-agent-models: \
	generate-anthropic-BootstrapFewShot-dspy-agent-model \
	generate-anthropic-BootstrapFewShotWithRandomSearch-dspy-agent-model \
	generate-anthropic-COPRO-dspy-agent-model \
	generate-anthropic-MIPROv2-dspy-agent-model

generate-gemini-%-dspy-agent-model: ## Generate DSPy agent model for Gemini analyses
	@echo "$(BLUE)Generating DSPy agent model for Gemini analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model gemini \
	--optimizer $* \
	--output output/dspy_models/guarino_gemini_$*_agent_model.json

generate-gemini-dspy-agent-models: \
	generate-gemini-BootstrapFewShot-dspy-agent-model \
	generate-gemini-BootstrapFewShotWithRandomSearch-dspy-agent-model \
	generate-gemini-COPRO-dspy-agent-model \
	generate-gemini-MIPROv2-dspy-agent-model

generate-gemma9b-%-dspy-agent-model: ## Generate DSPy agent model for Gemma 9B analyses
	@echo "$(BLUE)Generating DSPy agent model for Gemma 9B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model gemma9b \
	--optimizer $* \
	--output output/dspy_models/guarino_gemma9b_$*_agent_model.json

generate-gemma9b-dspy-agent-models: \
	generate-gemma9b-BootstrapFewShot-dspy-agent-model \
	generate-gemma9b-BootstrapFewShotWithRandomSearch-dspy-agent-model \
	generate-gemma9b-COPRO-dspy-agent-model \
	generate-gemma9b-MIPROv2-dspy-agent-model

generate-qwen7b-%-dspy-agent-model: ## Generate DSPy agent model for Qwen 7B analyses
	@echo "$(BLUE)Generating DSPy agent model for Qwen 7B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model qwen7b \
	--optimizer $* \
	--output output/dspy_models/guarino_qwen7b_$*_agent_model.json

generate-qwen7b-dspy-agent-models: \
	generate-qwen7b-BootstrapFewShot-dspy-agent-model \
	generate-qwen7b-BootstrapFewShotWithRandomSearch-dspy-agent-model \
	generate-qwen7b-COPRO-dspy-agent-model \
	generate-qwen7b-MIPROv2-dspy-agent-model

generate-llama8b-%-dspy-agent-model: ## Generate DSPy agent model for LLaMA 8B analyses
	@echo "$(BLUE)Generating DSPy agent model for LLaMA 8B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model llama8b \
	--optimizer $* \
	--output output/dspy_models/guarino_llama8b_$*_agent_model.json

generate-llama8b-dspy-agent-models: \
	generate-llama8b-BootstrapFewShot-dspy-agent-model \
	generate-llama8b-BootstrapFewShotWithRandomSearch-dspy-agent-model \
	generate-llama8b-COPRO-dspy-agent-model \
	generate-llama8b-MIPROv2-dspy-agent-model

generate-llama3b-%-dspy-agent-model: ## Generate DSPy agent model for LLaMA 3B analyses
	@echo "$(BLUE)Generating DSPy agent model for LLaMA 3B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model llama3b \
	--optimizer $* \
	--output output/dspy_models/guarino_llama3b_$*_agent_model.json

generate-llama3b-dspy-agent-models: \
	generate-llama3b-BootstrapFewShot-dspy-agent-model \
	generate-llama3b-BootstrapFewShotWithRandomSearch-dspy-agent-model \
	generate-llama3b-COPRO-dspy-agent-model \
	generate-llama3b-MIPROv2-dspy-agent-model

generate-gpt4o-mini-%-dspy-agent-model: ## Generate DSPy agent model for GPT-4o Mini analyses
	@echo "$(BLUE)Generating DSPy agent model for GPT-4o Mini analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model gpt4o-mini \
	--optimizer $* \
	--output output/dspy_models/guarino_gpt4o-mini_$*_agent_model.json

generate-gpt4o-mini-dspy-agent-models: \
	generate-gpt4o-mini-BootstrapFewShot-dspy-agent-model \
	generate-gpt4o-mini-BootstrapFewShotWithRandomSearch-dspy-agent-model \
	generate-gpt4o-mini-COPRO-dspy-agent-model \
	generate-gpt4o-mini-MIPROv2-dspy-agent-model

generate-llama70b-%-dspy-agent-model: ## Generate DSPy agent model for LLaMA 3.3 70B analyses
	@echo "$(BLUE)Generating DSPy agent model for LLaMA 3.3 70B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model llama70b \
	--optimizer $* \
	--output output/dspy_models/guarino_llama70b_$*_agent_model.json

generate-llama70b-dspy-agent-models: \
	generate-llama70b-BootstrapFewShot-dspy-agent-model \
	generate-llama70b-BootstrapFewShotWithRandomSearch-dspy-agent-model \
	generate-llama70b-COPRO-dspy-agent-model \
	generate-llama70b-MIPROv2-dspy-agent-model

generate-mistral-small-%-dspy-agent-model: ## Generate DSPy agent model for Mistral Small analyses
	@echo "$(BLUE)Generating DSPy agent model for Mistral Small analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model mistral-small-3.1 \
	--optimizer $* \
	--output output/dspy_models/guarino_mistral-small_$*_agent_model.json

generate-mistral-small-dspy-agent-models: \
	generate-mistral-small-BootstrapFewShot-dspy-agent-model \
	generate-mistral-small-BootstrapFewShotWithRandomSearch-dspy-agent-model \
	generate-mistral-small-COPRO-dspy-agent-model \
	generate-mistral-small-MIPROv2-dspy-agent-model

generate-qwen72b-%-dspy-agent-model: ## Generate DSPy agent model for Qwen 2.5 72B analyses
	@echo "$(BLUE)Generating DSPy agent model for Qwen 2.5 72B analyses...$(NC)"
	uv run python scripts/generate_dspy_agent_model.py $(TRAIN_FILE) $(TEST_FILE) --model qwen72b \
	--optimizer $* \
	--output output/dspy_models/guarino_qwen72b_$*_agent_model.json

generate-qwen72b-dspy-agent-models: \
	generate-qwen72b-BootstrapFewShot-dspy-agent-model \
	generate-qwen72b-BootstrapFewShotWithRandomSearch-dspy-agent-model \
	generate-qwen72b-COPRO-dspy-agent-model \
	generate-qwen72b-MIPROv2-dspy-agent-model

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
	generate-mistral-small-dspy-agent-models

##@ Batch Analysis Non-Agent DSPy Compiled Models
ONTOLOGY_FILE = output/ontologies/guarino_messy.owl
MODEL_DIR = output/dspy_models
ANALYZED_OUTPUT_DIR = output/analyzed_entities
EVALUATION_RESULTS_DIR = output/evaluation_results

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
	--output $(EVALUATION_RESULTS_DIR)/classify_dspy_$(1)_$(2)_$(3).json
endef

batch-non-agent-dspy-anthropic-%-gemma9b:
	$(call batch-non-agent-dspy,claude,$*,gemma9b)

batch-non-agent-dspy-anthropic-%-qwen7b:
	$(call batch-non-agent-dspy,claude,$*,qwen7b)

batch-non-agent-dspy-anthropic-%-llama8b:
	$(call batch-non-agent-dspy,claude,$*,llama8b)

batch-non-agent-dspy-anthropic-%-llama3b:
	$(call batch-non-agent-dspy,claude,$*,llama3b)

batch-non-agent-dspy-gemini-%-gemma9b:
	$(call batch-non-agent-dspy,gemini,$*,gemma9b)

batch-non-agent-dspy-gemini-%-qwen7b:
	$(call batch-non-agent-dspy,gemini,$*,qwen7b)

batch-non-agent-dspy-gemini-%-llama8b:
	$(call batch-non-agent-dspy,gemini,$*,llama8b)

batch-non-agent-dspy-gemini-%-llama3b:
	$(call batch-non-agent-dspy,gemini,$*,llama3b)

batch-non-agent-dspy-anthropic-%-gpt4o-mini:
	$(call batch-non-agent-dspy,claude,$*,gpt4o-mini)

batch-non-agent-dspy-anthropic-%-mistral-small-3.1:
	$(call batch-non-agent-dspy,claude,$*,mistral-small-3.1)

batch-non-agent-dspy-anthropic-%-llama70b:
	$(call batch-non-agent-dspy,claude,$*,llama70b)

batch-non-agent-dspy-anthropic-%-qwen72b:
	$(call batch-non-agent-dspy,claude,$*,qwen72b)

batch-non-agent-dspy-gemini-%-gpt4o-mini:
	$(call batch-non-agent-dspy,gemini,$*,gpt4o-mini)

batch-non-agent-dspy-gemini-%-mistral-small-3.1:
	$(call batch-non-agent-dspy,gemini,$*,mistral-small-3.1)

batch-non-agent-dspy-gemini-%-llama70b:
	$(call batch-non-agent-dspy,gemini,$*,llama70b)

batch-non-agent-dspy-gemini-%-qwen72b:
	$(call batch-non-agent-dspy,gemini,$*,qwen72b)

batch-non-agent-dspy-anthropic-small-models: \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-gemma9b \
	batch-non-agent-dspy-anthropic-BootstrapFewShotWithRandomSearch-gemma9b \
	batch-non-agent-dspy-anthropic-COPRO-gemma9b \
	batch-non-agent-dspy-anthropic-MIPROv2-gemma9b \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-qwen7b \
	batch-non-agent-dspy-anthropic-BootstrapFewShotWithRandomSearch-qwen7b \
	batch-non-agent-dspy-anthropic-COPRO-qwen7b \
	batch-non-agent-dspy-anthropic-MIPROv2-qwen7b \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-llama8b \
	batch-non-agent-dspy-anthropic-BootstrapFewShotWithRandomSearch-llama8b \
	batch-non-agent-dspy-anthropic-COPRO-llama8b \
	batch-non-agent-dspy-anthropic-MIPROv2-llama8b \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-llama3b \
	batch-non-agent-dspy-anthropic-BootstrapFewShotWithRandomSearch-llama3b \
	batch-non-agent-dspy-anthropic-COPRO-llama3b \
	batch-non-agent-dspy-anthropic-MIPROv2-llama3b \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-gpt4o-mini \
	batch-non-agent-dspy-anthropic-BootstrapFewShotWithRandomSearch-gpt4o-mini \
	batch-non-agent-dspy-anthropic-COPRO-gpt4o-mini \
	batch-non-agent-dspy-anthropic-MIPROv2-gpt4o-mini \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-mistral-small-3.1 \
	batch-non-agent-dspy-anthropic-BootstrapFewShotWithRandomSearch-mistral-small-3.1 \
	batch-non-agent-dspy-anthropic-COPRO-mistral-small-3.1 \
	batch-non-agent-dspy-anthropic-MIPROv2-mistral-small-3.1 \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-llama70b \
	batch-non-agent-dspy-anthropic-BootstrapFewShotWithRandomSearch-llama70b \
	batch-non-agent-dspy-anthropic-COPRO-llama70b \
	batch-non-agent-dspy-anthropic-MIPROv2-llama70b \
	batch-non-agent-dspy-anthropic-BootstrapFewShot-qwen72b \
	batch-non-agent-dspy-anthropic-BootstrapFewShotWithRandomSearch-qwen72b \
	batch-non-agent-dspy-anthropic-COPRO-qwen72b \
	batch-non-agent-dspy-anthropic-MIPROv2-qwen72b

batch-non-agent-dspy-gemini-small-models: \
	batch-non-agent-dspy-gemini-BootstrapFewShot-gemma9b \
	batch-non-agent-dspy-gemini-BootstrapFewShotWithRandomSearch-gemma9b \
	batch-non-agent-dspy-gemini-COPRO-gemma9b \
	batch-non-agent-dspy-gemini-MIPROv2-gemma9b \
	batch-non-agent-dspy-gemini-BootstrapFewShot-qwen7b \
	batch-non-agent-dspy-gemini-BootstrapFewShotWithRandomSearch-qwen7b \
	batch-non-agent-dspy-gemini-COPRO-qwen7b \
	batch-non-agent-dspy-gemini-MIPROv2-qwen7b \
	batch-non-agent-dspy-gemini-BootstrapFewShot-llama8b \
	batch-non-agent-dspy-gemini-BootstrapFewShotWithRandomSearch-llama8b \
	batch-non-agent-dspy-gemini-COPRO-llama8b \
	batch-non-agent-dspy-gemini-MIPROv2-llama8b \
	batch-non-agent-dspy-gemini-BootstrapFewShot-llama3b \
	batch-non-agent-dspy-gemini-BootstrapFewShotWithRandomSearch-llama3b \
	batch-non-agent-dspy-gemini-COPRO-llama3b \
	batch-non-agent-dspy-gemini-MIPROv2-llama3b \
	batch-non-agent-dspy-gemini-BootstrapFewShot-gpt4o-mini \
	batch-non-agent-dspy-gemini-BootstrapFewShotWithRandomSearch-gpt4o-mini \
	batch-non-agent-dspy-gemini-COPRO-gpt4o-mini \
	batch-non-agent-dspy-gemini-MIPROv2-gpt4o-mini \
	batch-non-agent-dspy-gemini-BootstrapFewShot-mistral-small-3.1 \
	batch-non-agent-dspy-gemini-BootstrapFewShotWithRandomSearch-mistral-small-3.1 \
	batch-non-agent-dspy-gemini-COPRO-mistral-small-3.1 \
	batch-non-agent-dspy-gemini-MIPROv2-mistral-small-3.1 \
	batch-non-agent-dspy-gemini-BootstrapFewShot-llama70b \
	batch-non-agent-dspy-gemini-BootstrapFewShotWithRandomSearch-llama70b \
	batch-non-agent-dspy-gemini-COPRO-llama70b \
	batch-non-agent-dspy-gemini-MIPROv2-llama70b \
	batch-non-agent-dspy-gemini-BootstrapFewShot-qwen72b \
	batch-non-agent-dspy-gemini-BootstrapFewShotWithRandomSearch-qwen72b \
	batch-non-agent-dspy-gemini-COPRO-qwen72b \
	batch-non-agent-dspy-gemini-MIPROv2-qwen72b

batch-non-agent-dspy-small-models: \
	batch-non-agent-dspy-anthropic-small-models \
	batch-non-agent-dspy-gemini-small-models

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

##@ Complete Workflows

reproduce-batch: batch-non-agent eval-non-agent classify-non-agent collect-non-agent batch-agent eval-agent classify-agent collect-agent batch-critic eval-critic classify-critic collect-critic batch-non-agent-expanded ## Run complete batch analysis reproduction with classification metrics (46 experiments + 20 classification evaluations)
	@echo "$(GREEN)Complete batch analysis reproduction finished!$(NC)"
	@echo "Reports available in docs/reports/"
	@echo "Classification metrics available in output/evaluation_results/classify_*.csv"
