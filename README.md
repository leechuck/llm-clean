# Guarino & Welty "Messy Taxonomy" Ontology

This project reproduces the "messy taxonomy" example (Figure 2) from the classic paper *"A Formal Ontology of Properties"* by Nicola Guarino and Christopher Welty (2000). It downloads the paper and formalizes the described taxonomy into an OWL ontology.

## Project Structure

*   `resources/`: Contains the downloaded PDF of the paper.
*   `ontology/`: Contains the generated OWL ontology (`guarino_messy.owl`).
*   `scripts/`: Python scripts for downloading the paper and generating the ontology.
*   `reproduce.sh`: A shell script to automate the entire process using `uv`.

## Prerequisites

*   **uv**: This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management and script execution. Ensure it is installed on your system.
    *   Installation: `curl -LsSf https://astral.sh/uv/install.sh | sh` (or see their official docs).

## Instructions

To reproduce the project (download the paper and generate the ontology):

1.  Make the reproduction script executable (if it isn't already):
    ```bash
    chmod +x reproduce.sh
    ```

2.  Run the reproduction script:
    ```bash
    ./reproduce.sh
    ```

This script will:
1.  Download the paper to `resources/01-guarino00formal.pdf` (if not already present).
2.  Install necessary Python dependencies (specifically `rdflib`) in an ephemeral environment.
3.  Generate the OWL ontology based on Figure 2 of the paper and save it to `ontology/guarino_messy.owl`.

## The Ontology

The generated ontology (`ontology/guarino_messy.owl`) represents the "messy" state of the taxonomy described in the paper, illustrating common ontological modeling errors such as confusing properties with classes and improper use of multiple inheritance (e.g., `RedApple` being a subclass of both `Apple` and `Red`).
