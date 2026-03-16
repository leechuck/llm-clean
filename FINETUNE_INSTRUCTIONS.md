# Fine-Tuning Instructions

Step-by-step guide to locally fine-tuning OntoClean property analysis models on Apple Silicon (macOS).

---

## Overview

The fine-tuning pipeline has two stages:

```
Stage 1: Generate training data
  data/raw/ground_truth.tsv
        ↓  generate_finetune_data.py  (LLM generates reasoning traces)
  output/fine-tunning/data/finetune_data.jsonl

Stage 2: Fine-tune each model
  finetune_data.jsonl
        ↓  finetune_local.py  (4 automated steps per model)
  output/fine-tunning/adapters/<model>-ontoclean/   ← LoRA adapter
  output/fine-tunning/models/<model>-ontoclean-fused/  ← merged model
  output/fine-tunning/models/<model>-ontoclean.gguf    ← GGUF for Ollama
  Ollama: <model>-ontoclean
```

---

## Prerequisites

### System
- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3.10+, [uv](https://github.com/astral-sh/uv) installed
- [Ollama](https://ollama.com) installed

### Install dependencies
```bash
uv sync
```

### API keys (for Stage 1 only)
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_key     # for --model gemini (default)
ANTHROPIC_API_KEY=your_key  # for --model anthropic (higher quality reasoning)
OPENROUTER_API_KEY=your_key # for full model names
```

### HuggingFace authentication (for gated models)
Llama and Gemma models require accepting a license agreement before download.

1. Visit the model page on [huggingface.co](https://huggingface.co) and click **"Agree and access repository"**
2. Create an access token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
3. Log in:
```bash
uv run huggingface-cli login
```

| Model | Gated? |
|-------|--------|
| `mistralai/Mistral-7B-Instruct-v0.3` | No |
| `Qwen/Qwen2.5-7B-Instruct` | No |
| `meta-llama/Llama-3.1-8B-Instruct` | **Yes** |
| `meta-llama/Llama-3.2-3B-Instruct` | **Yes** |
| `google/gemma-2-9b-it` | **Yes** |

---

## Stage 1 — Generate Training Data

The training data is derived from `data/raw/ground_truth.tsv` (22 authoritative labeled entities). A strong LLM generates reasoning traces for each entity; the ground-truth property values replace the LLM's predictions.

> **A pre-generated copy is already included** at `output/fine-tunning/data/finetune_data.jsonl`.
> Skip Stage 1 and go directly to Stage 2 unless you want to regenerate with a different model.

### Run

```bash
# Default: use Gemini to generate reasoning traces
uv run python scripts/generate_finetune_data.py

# Higher-quality reasoning with Anthropic Claude
uv run python scripts/generate_finetune_data.py --model anthropic

# Test the pipeline without making API calls
uv run python scripts/generate_finetune_data.py --skip-reasoning
```

### Output

`output/fine-tunning/data/finetune_data.jsonl` — 22 JSONL records in chat format:

```json
{
  "messages": [
    {"role": "system", "content": "<OntoClean system prompt>"},
    {"role": "user",   "content": "Term: Butterfly\nDescription: \nUsage: "},
    {"role": "assistant", "content": "{\"properties\": {\"rigidity\": \"~R\", ...}, \"reasoning\": \"...\"}"}
  ]
}
```

The assistant response always uses the **ground-truth property values** regardless of what the LLM predicted, so the training data is authoritative.

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--ground-truth` | `data/raw/ground_truth.tsv` | Source of property labels |
| `--output` | `output/fine-tunning/data/finetune_data.jsonl` | Output JSONL path |
| `--model` | `gemini` | LLM for reasoning generation (`gemini`, `anthropic`, etc.) |
| `--delay` | `1.0` | Seconds between API calls |
| `--skip-reasoning` | off | Generate data without API calls (uses placeholder reasoning) |

---

## Stage 2 — Fine-Tune Models

`scripts/finetune_local.py` runs four steps for each model:

| Step | Tool | What happens |
|------|------|--------------|
| 1 — Download & convert | `mlx_lm.convert` | Downloads model from HuggingFace, converts to MLX format |
| 2 — LoRA fine-tune | `mlx_lm.lora` | Trains LoRA adapter on `finetune_data.jsonl` |
| 3 — Fuse + export GGUF | `mlx_lm.fuse` + `export_gguf.py` | Merges adapter into base model; exports GGUF |
| 4 — Register | `ollama create` | Registers GGUF with Ollama |

Each step is **skipped automatically** if its output already exists (safe to resume after interruption).

### Hyperparameters

With 22 training examples (`batch_size=4` → ~5 steps/epoch):

| Parameter | Default | Notes |
|-----------|---------|-------|
| `--iters` | `100` | ~18 epochs. Use 100–200 for small datasets. 600+ causes severe overfitting. |
| `--lr` | `2e-5` | Conservative for small datasets. Use `1e-4` for 200+ examples. |
| `--num-layers` | `8` | Number of LoRA layers to train. |

---

## Fine-Tuning Each Model

### Mistral 7B

```bash
make finetune-mistral7b
```

Or directly:
```bash
uv run python scripts/finetune_local.py \
    --hf-model mistralai/Mistral-7B-Instruct-v0.3 \
    --mlx-path output/fine-tunning/models/mistral-7b-mlx \
    --data output/fine-tunning/data/finetune_data.jsonl \
    --adapter output/fine-tunning/adapters/mistral7b-ontoclean \
    --fused output/fine-tunning/models/mistral7b-ontoclean-fused \
    --gguf output/fine-tunning/models/mistral7b-ontoclean.gguf \
    --ollama-name mistral7b-ontoclean
```

Outputs:
- `output/fine-tunning/adapters/mistral7b-ontoclean/` — LoRA adapter
- `output/fine-tunning/models/mistral7b-ontoclean-fused/` — merged model
- `output/fine-tunning/models/mistral7b-ontoclean.gguf` — GGUF

---

### Gemma 9B

> Requires HuggingFace login and license acceptance at [huggingface.co/google/gemma-2-9b-it](https://huggingface.co/google/gemma-2-9b-it)
>
> Uses `--no-system-role` because Gemma's chat template rejects the `system` role.
> The system prompt is automatically merged into the first user message.

```bash
make finetune-gemma9b
```

Or directly:
```bash
uv run python scripts/finetune_local.py \
    --hf-model google/gemma-2-9b-it \
    --mlx-path output/fine-tunning/models/gemma-9b-mlx \
    --data output/fine-tunning/data/finetune_data.jsonl \
    --adapter output/fine-tunning/adapters/gemma9b-ontoclean \
    --fused output/fine-tunning/models/gemma9b-ontoclean-fused \
    --gguf output/fine-tunning/models/gemma9b-ontoclean.gguf \
    --ollama-name gemma9b-ontoclean \
    --no-system-role
```

---

### Qwen 7B

```bash
make finetune-qwen7b
```

Or directly:
```bash
uv run python scripts/finetune_local.py \
    --hf-model Qwen/Qwen2.5-7B-Instruct \
    --mlx-path output/fine-tunning/models/qwen2.5-7b-mlx \
    --data output/fine-tunning/data/finetune_data.jsonl \
    --adapter output/fine-tunning/adapters/qwen7b-ontoclean \
    --fused output/fine-tunning/models/qwen7b-ontoclean-fused \
    --gguf output/fine-tunning/models/qwen7b-ontoclean.gguf \
    --ollama-name qwen7b-ontoclean
```

---

### Llama 8B

> Requires HuggingFace login and license acceptance at [huggingface.co/meta-llama/Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)

```bash
make finetune-llama8b
```

Or directly:
```bash
uv run python scripts/finetune_local.py \
    --hf-model meta-llama/Llama-3.1-8B-Instruct \
    --mlx-path output/fine-tunning/models/llama-8b-mlx \
    --data output/fine-tunning/data/finetune_data.jsonl \
    --adapter output/fine-tunning/adapters/llama8b-ontoclean \
    --fused output/fine-tunning/models/llama8b-ontoclean-fused \
    --gguf output/fine-tunning/models/llama8b-ontoclean.gguf \
    --ollama-name llama8b-ontoclean
```

---

### Llama 3B

> Requires HuggingFace login and license acceptance at [huggingface.co/meta-llama/Llama-3.2-3B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct)

```bash
make finetune-llama3b
```

Or directly:
```bash
uv run python scripts/finetune_local.py \
    --hf-model meta-llama/Llama-3.2-3B-Instruct \
    --mlx-path output/fine-tunning/models/llama-3b-mlx \
    --data output/fine-tunning/data/finetune_data.jsonl \
    --adapter output/fine-tunning/adapters/llama3b-ontoclean \
    --fused output/fine-tunning/models/llama3b-ontoclean-fused \
    --gguf output/fine-tunning/models/llama3b-ontoclean.gguf \
    --ollama-name llama3b-ontoclean
```

---

### Fine-tune all five

```bash
make finetune-all-local
```

This runs all five targets sequentially. Allow several hours depending on hardware.

---

## Resuming an Interrupted Run

Each step checks whether its output already exists and skips if so. To resume:

```bash
# Skip steps that completed successfully
uv run python scripts/finetune_local.py --skip-download --skip-train [other args]
```

To force a step to re-run, delete its output:

```bash
# Re-run training only (keep downloaded model)
rm -rf output/fine-tunning/adapters/mistral7b-ontoclean
uv run python scripts/finetune_local.py --skip-download [other args]

# Re-run fuse + GGUF only
rm -rf output/fine-tunning/models/mistral7b-ontoclean-fused
rm -f  output/fine-tunning/models/mistral7b-ontoclean.gguf
uv run python scripts/finetune_local.py --skip-download --skip-train [other args]
```

---

## Dry Run (Preview Without Executing)

```bash
uv run python scripts/finetune_local.py --dry-run
uv run python scripts/finetune_local.py --hf-model Qwen/Qwen2.5-7B-Instruct --dry-run
```

---

## Hardware Requirements

| Model | Min unified RAM | Approximate download | Training time (M3 Pro) |
|-------|----------------|----------------------|------------------------|
| Llama 3.2-3B | ~8 GB | ~6 GB | ~15 min |
| Mistral 7B | ~16 GB | ~15 GB | ~30 min |
| Qwen2.5-7B | ~16 GB | ~15 GB | ~30 min |
| Llama 3.1-8B | ~16 GB | ~16 GB | ~30 min |
| Gemma 2-9B | ~20 GB | ~18 GB | ~45 min |

---

## Testing the Fine-Tuned Models

After fine-tuning, evaluate each model against `guarino_messy.owl` and `ground_truth.tsv`.
The test scripts start `mlx_lm.server` automatically, run the evaluation, and shut it down.

```bash
make test-finetuned-mistral7b
make test-finetuned-gemma9b
make test-finetuned-qwen7b
make test-finetuned-llama8b
make test-finetuned-llama3b
make test-finetuned-all        # run all five sequentially
```

Results are written to `output/finetuned_tests/<model>_ontoclean_results.tsv`.

### Evaluation results (100 iters, lr=2e-5, 22 training examples)

| Model | Overall | Rigidity | Identity | Own Identity | Unity | Dependence |
|-------|---------|----------|----------|--------------|-------|------------|
| `qwen7b` | **74.5%** | 16/22 | 20/22 | 16/22 | 13/22 | 17/22 |
| `llama8b` | 70.0% | 15/22 | 19/22 | 13/22 | 13/22 | 17/22 |
| `gemma9b` | 52.7% | 10/22 | 18/22 | 5/22 | 11/22 | 14/22 |
| `llama3b` | 49.1% | 15/22 | 11/22 | 9/22 | 9/22 | 10/22 |
| `mistral7b` | 47.3% | 4/22 | 13/22 | 9/22 | 11/22 | 15/22 |

---

## Troubleshooting

### "No endpoints found" / 404 on OpenRouter
The HuggingFace model ID (for local fine-tuning) differs from the OpenRouter model ID (for inference). The scripts handle this automatically via the shortcut mapping in `dspy_analyzer.py`.

### "System role not supported" (Gemma)
Always pass `--no-system-role` when fine-tuning or testing Gemma. The Makefile targets do this automatically.

### Garbled/repetitive model output
The model was overtrained. Delete the adapter and retrain with fewer iterations:
```bash
rm -rf output/fine-tunning/adapters/<model>-ontoclean
# Default is already 100 iters / lr=2e-5; reduce further if needed:
uv run python scripts/finetune_local.py --skip-download --iters 50 --lr 1e-5 [other args]
```

### "Address already in use" (port 8080)
A previous `mlx_lm.server` process is still running:
```bash
lsof -ti :8080 | xargs kill -9
```

### GGUF export "can only serialize row-major arrays"
This is a known `mlx_lm` bug fixed by `scripts/export_gguf.py`, which is called automatically by `finetune_local.py`. You do not need to run it manually.

### Ollama model crash (500 Internal Server Error)
The GGUF export has incorrect architecture metadata for non-LLaMA models. Use `mlx_lm.server` directly (via `test_with_mlx_server.py`) instead of Ollama for testing. The Makefile test targets handle this automatically.
