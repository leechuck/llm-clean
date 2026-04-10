#!/bin/bash
#SBATCH --job-name=ncit-infer-bfo3
#SBATCH --account=pi-hohndor
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=80G
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00
#SBATCH --output=/ibex/scratch/projects/c2014/rob/ontoclean/logs/infer_ncit_bfo3_%j.out
#SBATCH --error=/ibex/scratch/projects/c2014/rob/ontoclean/logs/infer_ncit_bfo3_%j.err

set -euo pipefail

REPO=/home/hohndor/llm-clean
SCRATCH=/ibex/scratch/projects/c2014/rob/ontoclean
ENTITIES_TSV="$REPO/ncit_top300_entities.tsv"
MODEL_DIR="$SCRATCH/models/qwen7b-ontoclean/merged"
OUTPUT_TSV="$SCRATCH/ncit_top300_ontoclean_predictions_bfo3.tsv"

mkdir -p "$SCRATCH/logs"

module purge
module load python/3.11.0

VENV="$SCRATCH/venv"
source "$VENV/bin/activate"

export HF_HOME="$SCRATCH/hf_cache"
export TRANSFORMERS_CACHE="$SCRATCH/hf_cache"

echo "=== OntoClean Inference on NCIt top-300 (BFO v3 prompt) ==="
echo "Job ID:  $SLURM_JOB_ID"
echo "Node:    $SLURMD_NODENAME"
echo "Entities: $ENTITIES_TSV"
echo "Model:    $MODEL_DIR"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

python "$REPO/ibex/infer_ontoclean_ibex_bfo3.py" \
    --input   "$ENTITIES_TSV" \
    --model   "$MODEL_DIR" \
    --output  "$OUTPUT_TSV"

echo "=== Inference complete. Results at $OUTPUT_TSV ==="
