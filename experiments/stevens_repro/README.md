# Stevens et al. (2019) Reproduction Study

This directory contains the code and data for reproducing the experiment described in:
*Stevens, R., Lord, P., Malone, J., & Matentzoglu, N. (2019). Measuring expert performance at manually classifying domain entities under upper ontology classes. Web Semantics: Science, Services and Agents on the World Wide Web, 57, 100469.*

The goal is to evaluate the performance of Large Language Models (LLMs) in classifying the same 46 domain entities (from the travel domain) into classes of three upper ontologies: **BFO**, **DOLCE**, and **UFO**.

## Methodology

The experiment employs two classification strategies:
1.  **Hierarchical**: The LLM traverses the ontology tree from the root, selecting the best subclass at each level until it reaches a leaf or decides the current class is the best fit.
2.  **One-Shot**: The LLM is presented with all classes of the ontology at once and asked to select the single best class.

Both strategies are provided with:
*   The term and its description (as used in the original paper or reconstructed).
*   Definitions of the candidate ontology classes.
*   Examples of instances for those classes (where available).

## Directory Structure

*   `data/`: Input data and ontology definitions.
    *   `input_terms.json`: The 46 travel domain entities.
    *   `ontologies.json`: Definitions, hierarchy, and examples for BFO, DOLCE, and UFO.
    *   `raw_entities.tsv`: Original extracted list.
*   `results/`: Experiment outputs.
    *   `experiment_results.json`: Full detailed JSON results including reasoning traces.
    *   `experiment_results.tsv`: Tabular summary for analysis.
*   `scripts/`: Python scripts for running the experiment.
    *   `run_experiment.py`: Main driver script.
    *   `results_to_tsv.py`: Helper to convert JSON results to TSV.
    *   `prepare_data.py`: Helper to generate input JSON from raw TSV.

## Usage

1.  **Run the Experiment**:
    ```bash
    # Run on all terms
    python3 experiments/stevens_repro/scripts/run_experiment.py --model openai/gpt-4o

    # Run on a subset (e.g., first 5) for testing
    python3 experiments/stevens_repro/scripts/run_experiment.py --limit 5
    ```

2.  **Generate Report**:
    ```bash
    python3 experiments/stevens_repro/scripts/results_to_tsv.py
    ```
    This updates `results/experiment_results.tsv`.

## Configuration

*   **API Key**: Ensure `OPENROUTER_API_KEY` is set in your environment.
*   **Ontologies**: You can modify `data/ontologies.json` to add more classes, improve definitions, or add examples to guide the LLM.
