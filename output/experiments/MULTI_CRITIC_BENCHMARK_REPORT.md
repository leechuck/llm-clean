# Multi-Critic vs Single-Critic Benchmark

**Date**: 2026-03-09

## Experiment Design

### Research Question

Does decomposing the OntoClean critic into 4 specialized property-critics (one per meta-property) improve taxonomy quality compared to a single monolithic critic? And does the rejection threshold (strict t=1 vs majority-vote t=2) matter?

### Architecture

All workflows share the same **Taxonomist agent** (proposes IS-A links) and the same propose-critique-retry loop (max 3 attempts per term). They differ only in the critic stage:

- **Single-Critic** (`OntoCleanWorkflow` in `src/llm_clean/agents/workflow.py`): One critic checks all OntoClean constraints (rigidity, identity, unity) in a single prompt.
- **Multi-strict (t=1)** (`MultiCriticWorkflow`, threshold=1): Four independent critics, each checking one property, run sequentially per proposal. A link is rejected if **any single critic** rejects it.
- **Multi-majority (t=2)** (`MultiCriticWorkflow`, threshold=2): Same four critics, but a link is rejected only when **≥2 critics** reject it (majority vote). All rejection feedback is aggregated and passed back to the taxonomist for retry.

### Critic Prompts

The four property-specific critic prompts are defined in `src/llm_clean/agents/critic_prompts.py`:

| Critic | Property | Constraint Checked |
|--------|----------|--------------------|
| Rigidity | +R / -R / ~R | ~R (anti-rigid) cannot subsume +R (rigid) |
| Identity | +I / -I | +I (sortal) cannot subsume -I (non-sortal) |
| Unity | +U / -U / ~U | ~U (anti-unity) cannot subsume +U (whole) |
| Dependence | +D / -D | -D subsumes +D signals role/relational confusion |

### Models Tested

All models accessed via OpenRouter API. The same model serves as both taxonomist and critic(s).

| Model | OpenRouter ID |
|-------|---------------|
| Llama 3.2 3B | `meta-llama/llama-3.2-3b-instruct` |
| Llama 3.1 8B | `meta-llama/llama-3.1-8b-instruct` |
| Qwen 2.5 7B | `qwen/qwen-2.5-7b-instruct` |

### Dataset

`data/benchmark_10_domains.json` — 10 domains, each with ~35 terms and ground-truth OntoClean properties.

Domains: Treatment of bronchitis, Cycling, Naval Warfare, eCommerce, Myrmecology, High-Frequency Trading, Urban Parkour, Quantum Computing, Sourdough Baking, Wastewater Treatment.

### Evaluation Metrics

- **Total Links**: Number of IS-A links in the generated taxonomy (higher = richer taxonomy)
- **Violations**: Critical OntoClean rigidity constraint violations (rigid child under anti-rigid parent) — lower is better
- **Cycles**: Circular IS-A chains detected in the taxonomy — lower is better
- **Warnings**: Potential constitution traps (object classified under material) — lower is better

---

## Full Results

| Model        | Critic Type           | Links | Violations | Cycles | Warnings |
|:-------------|:----------------------|------:|-----------:|-------:|---------:|
| Llama 3.1 8B | Single                |   225 |          1 |      6 |        2 |
| Llama 3.1 8B | Multi-majority (t=2)  |    74 |          0 |      0 |        0 |
| Llama 3.1 8B | Multi-strict (t=1)    |     8 |          0 |      0 |        0 |
| Llama 3.2 3B | Single                |   160 |          0 |      6 |        1 |
| Llama 3.2 3B | Multi-majority (t=2)  |   180 |          1 |     12 |        3 |
| Llama 3.2 3B | Multi-strict (t=1)    |   112 |          0 |     10 |        0 |
| Qwen 2.5 7B  | Single                |   255 |          3 |     15 |        3 |
| Qwen 2.5 7B  | Multi-majority (t=2)  |   219 |          0 |     10 |        1 |
| Qwen 2.5 7B  | Multi-strict (t=1)    |    93 |          1 |      1 |        0 |

---

## Delta Summary (Multi − Single, negative = improvement)

| Model        | Critic Type          | ΔLinks | ΔViolations | ΔCycles | ΔWarnings |
|:-------------|:---------------------|-------:|------------:|--------:|----------:|
| Llama 3.1 8B | Multi-majority (t=2) |   -151 |          -1 |      -6 |        -2 |
| Llama 3.1 8B | Multi-strict (t=1)   |   -217 |          -1 |      -6 |        -2 |
| Llama 3.2 3B | Multi-majority (t=2) |    +20 |          +1 |      +6 |        +2 |
| Llama 3.2 3B | Multi-strict (t=1)   |    -48 |           0 |      +4 |        -1 |
| Qwen 2.5 7B  | Multi-majority (t=2) |    -36 |          -3 |      -5 |        -2 |
| Qwen 2.5 7B  | Multi-strict (t=1)   |   -162 |          -2 |     -14 |        -3 |

---

## Analysis

### Model-by-Model

**Llama 3.2 3B (3B parameters)**

- **Single critic** already produces a reasonably clean result: 0 violations, 6 cycles, 1 warning.
- **Multi-majority (t=2)** *degrades* quality across the board: +1 violation, +6 cycles, +2 warnings, and slightly more links. The 3B model's individual critics are too unreliable — they approve bad proposals when only 2-of-4 need to agree.
- **Multi-strict (t=1)** partially helps: violations stay at 0, warnings drop to 0, link count drops moderately (−48). However, cycles *increase* (+4), suggesting the strict threshold still passes through structurally broken proposals.
- **Conclusion**: The 3B model lacks sufficient reasoning capacity to apply decomposed OntoClean analysis reliably. Multi-critic does not consistently help and can hurt.

**Llama 3.1 8B (8B parameters)**

- **Single critic** has moderate quality: 1 violation, 6 cycles, 2 warnings.
- **Multi-majority (t=2)** eliminates all problems (0 violations, 0 cycles, 0 warnings) but at a steep coverage cost: only 74 links remain vs 225 (−67%).
- **Multi-strict (t=1)** is even more aggressive: just 8 links total across all 10 domains — the critics reject almost everything. Quality is perfect but the taxonomy is essentially empty.
- **Conclusion**: The 8B model's critics are accurate but extremely conservative. The majority threshold (t=2) strikes the better quality/coverage trade-off; t=1 is too strict to be useful.

**Qwen 2.5 7B (7B parameters)**

- **Single critic** has the worst raw quality: 3 violations, 15 cycles, 3 warnings — but the most links (255).
- **Multi-majority (t=2)** greatly improves quality (−3 violations, −5 cycles, −2 warnings) while preserving most coverage (219 links, −14%). This is the best overall result.
- **Multi-strict (t=1)** eliminates nearly all cycles (just 1 remaining, down from 15) and all warnings, but introduces 1 new violation and drops coverage significantly (93 links, −63%).
- **Conclusion**: Qwen 2.5 7B benefits most clearly from multi-critic. The majority threshold (t=2) is the sweet spot — large quality gains with minimal coverage loss.

### Cross-Model Patterns

1. **Model size and critic reliability**: The 3B model's critics are too noisy for decomposed reasoning. Both 7B and 8B models produce critics accurate enough to improve quality when using t=2.

2. **Threshold matters critically**: t=2 (majority) consistently outperforms t=1 (strict) in the quality/coverage trade-off. t=1 over-rejects — particularly for the 8B model (8 links total is unusable) — while t=2 retains substantially more taxonomy structure.

3. **Violation elimination**: Both 7B+ models eliminate all violations (or near-all) under t=2. The 3B model cannot.

4. **Cycle reduction**: Cycles are reduced by t=2 for 8B (−6) and 7B (−5) but worsen for 3B (+6). Cycles are a harder structural problem — even specialised critics struggle without global graph awareness.

5. **Best overall configuration**: **Qwen 2.5 7B + Multi-majority (t=2)** — zero violations, 10 remaining cycles (down from 15), 1 warning (down from 3), and 219 links (86% of single-critic coverage).

### Summary: Best Configuration per Model

| Model        | Best Config          | Violations | Cycles | Warnings | Links (% of Single) |
|:-------------|:---------------------|-----------:|-------:|---------:|--------------------:|
| Llama 3.2 3B | Single (baseline)    |          0 |      6 |        1 | 100% (160)          |
| Llama 3.1 8B | Multi-majority (t=2) |          0 |      0 |        0 | 33% (74)            |
| Qwen 2.5 7B  | Multi-majority (t=2) |          0 |     10 |        1 | 86% (219)           |

---

## Reproducibility

```bash
# Single model, single-critic
uv run python scripts/agentic_taxonomy.py data/benchmark_10_domains.json \
  output/experiments/taxonomy_agentic_<slug>.json --model <openrouter-id>

# Single model, multi-critic (majority, t=2)
uv run python scripts/agentic_taxonomy_multi_critic.py data/benchmark_10_domains.json \
  output/experiments/taxonomy_agentic_multi_critic_<slug>.json --model <openrouter-id> --threshold 2

# Single model, multi-critic (strict, t=1)
uv run python scripts/agentic_taxonomy_multi_critic.py data/benchmark_10_domains.json \
  output/experiments/taxonomy_agentic_multi_critic_t1_<slug>.json --model <openrouter-id> --threshold 1

# Full benchmark (skips existing results)
uv run python scripts/run_multi_critic_benchmark.py

# Evaluate any taxonomy file
uv run python scripts/evaluate_taxonomy.py data/benchmark_10_domains.json <taxonomy-file>.json
```

### Output Files

| File | Description |
|------|-------------|
| `output/experiments/taxonomy_agentic_llama-3.2-3b-instruct.json` | Single, Llama 3.2 3B |
| `output/experiments/taxonomy_agentic_llama-3.1-8b-instruct.json` | Single, Llama 3.1 8B |
| `output/experiments/taxonomy_agentic_qwen-2.5-7b-instruct.json` | Single, Qwen 2.5 7B |
| `output/experiments/taxonomy_agentic_multi_critic_llama-3.2-3b-instruct.json` | Multi t=2, Llama 3.2 3B |
| `output/experiments/taxonomy_agentic_multi_critic_llama-3.1-8b-instruct.json` | Multi t=2, Llama 3.1 8B |
| `output/experiments/taxonomy_agentic_multi_critic_qwen-2.5-7b-instruct.json` | Multi t=2, Qwen 2.5 7B |
| `output/experiments/taxonomy_agentic_multi_critic_t1_llama-3.2-3b-instruct.json` | Multi t=1, Llama 3.2 3B |
| `output/experiments/taxonomy_agentic_multi_critic_t1_llama-3.1-8b-instruct.json` | Multi t=1, Llama 3.1 8B |
| `output/experiments/taxonomy_agentic_multi_critic_t1_qwen-2.5-7b-instruct.json` | Multi t=1, Qwen 2.5 7B |
