#!/bin/bash
set -e

# Ensure dependencies are available for the scripts
# Using uv run with --with to ensure rdflib is available for the ontology script

echo "Running download script..."
uv run scripts/download_paper.py --url "http://cui.unige.ch/isi/cours/aftsi/articles/01-guarino00formal.pdf" --output "resources/01-guarino00formal.pdf"

echo "Running ontology generation script..."
uv run --with rdflib scripts/generate_messy_owl.py --output "ontology/guarino_messy.owl"

echo "Done. Ontology saved to ontology/guarino_messy.owl"