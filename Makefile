.PHONY: help all clean setup directories \
        download-paper generate-owl \
        benchmark-zeroshot benchmark-agentic \
        batch-non-agent batch-non-agent-claude batch-non-agent-gemini \
        batch-agent batch-agent-claude batch-agent-gemini \
        batch-critic batch-critic-claude batch-critic-gemini \
        eval-non-agent eval-non-agent-claude eval-non-agent-gemini \
        eval-agent eval-agent-claude eval-agent-gemini \
        eval-critic eval-critic-claude eval-critic-gemini \
        collect-non-agent collect-agent collect-critic \
        reports reproduce-static reproduce-batch

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

reports: collect-non-agent collect-agent collect-critic ## Generate all analysis reports

##@ Complete Workflows

reproduce-batch: batch-non-agent eval-non-agent collect-non-agent batch-agent eval-agent collect-agent batch-critic eval-critic collect-critic ## Run complete batch analysis reproduction (20 experiments)
	@echo "$(GREEN)Complete batch analysis reproduction finished!$(NC)"
	@echo "Reports available in docs/reports/"
