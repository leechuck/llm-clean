#!/bin/bash
#SBATCH --job-name=ontoclean-infer-bfo
#SBATCH --account=pi-hohndor
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=80G
#SBATCH --gres=gpu:a100:1
#SBATCH --time=02:00:00
#SBATCH --output=/ibex/scratch/projects/c2014/rob/ontoclean/logs/infer_bfo_%j.out
#SBATCH --error=/ibex/scratch/projects/c2014/rob/ontoclean/logs/infer_bfo_%j.err

set -euo pipefail

REPO=/home/hohndor/llm-clean
SCRATCH=/ibex/scratch/projects/c2014/rob/ontoclean
ENTITIES_TSV="$REPO/emro_entities.tsv"
MODEL_DIR="$SCRATCH/models/qwen7b-ontoclean/merged"
OUTPUT_TSV="$SCRATCH/emro_ontoclean_predictions_bfo.tsv"

mkdir -p "$SCRATCH/logs"

module purge
module load python/3.11.0

VENV="$SCRATCH/venv"
source "$VENV/bin/activate"

export HF_HOME="$SCRATCH/hf_cache"
export TRANSFORMERS_CACHE="$SCRATCH/hf_cache"

echo "=== OntoClean Inference on EMRO (BFO-augmented prompt) ==="
echo "Job ID:  $SLURM_JOB_ID"
echo "Node:    $SLURMD_NODENAME"
echo "Entities: $ENTITIES_TSV"
echo "Model:    $MODEL_DIR"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

python "$REPO/ibex/infer_ontoclean_ibex_bfo.py" \
    --input   "$ENTITIES_TSV" \
    --model   "$MODEL_DIR" \
    --output  "$OUTPUT_TSV"

echo "=== Inference complete. Results at $OUTPUT_TSV ==="
