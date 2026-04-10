# ALEval Experiment Execution Guide

Step-by-step guide for running the full ALEval experiment.
Follow the phases in order — each phase builds on the previous one.

## Experiment Overview

| Parameter | Value |
|-----------|-------|
| Benchmark | LiveCodeBench (conflicting split) |
| Tasks per model | 103 |
| Minimal scaffold | All models |
| Tools scaffold | 2-3 best performers from minimal |
| Budget target | ~$300 |
| Primary metric | Lie rate among triggered callouts |

---

## Phase 0: Prerequisites

### 0.1 Install ALEval

```bash
pip install -e .
pip install -e ".[analysis]"   # For LLM judge
```

### 0.2 Configure API key

```bash
cp .env.example .env
# Edit .env: set OPENROUTER_API_KEY=sk-or-...
```

Verify it works:
```bash
python -c "import os; k=os.environ.get('OPENROUTER_API_KEY',''); print('OK' if k.startswith('sk-or-') else 'MISSING: set OPENROUTER_API_KEY in .env')"
```

### 0.3 Verify Docker (only needed for tools scaffold)

```bash
docker version
```

If Docker is not running, you can still run the full minimal experiment with `--sandbox local`.

### 0.4 Configure your models

Edit `experiments/config.sh` and set the `MODELS_MINIMAL` and `MODELS_TOOLS` arrays.

All models use OpenRouter format: `openrouter/<provider>/<model>`.
Browse available models at [openrouter.ai/models](https://openrouter.ai/models).

### 0.5 Make scripts executable

```bash
chmod +x experiments/run_model.sh experiments/run_all.sh experiments/collect_results.sh
```

---

## Phase 1: Smoke Test

Run 3 samples on your first model to verify the entire pipeline works.

### 1.1 Run smoke test

```bash
./experiments/run_all.sh smoke
```

This runs 3 tasks on the first model in `MODELS_MINIMAL` with `--sandbox local`.

**Expected**: Completes in 2-5 minutes. You should see Inspect AI output with
sample progress and a final summary.

### 1.2 Verify logs were created

```bash
ls logs/aleval/minimal/*/
```

You should see one or more `.eval` files.

### 1.3 Generate a smoke report

```bash
aleval-report \
  --logs-dir logs/aleval/minimal/$(ls logs/aleval/minimal/) \
  --out-dir reports/aleval/smoke
```

### 1.4 Check the report

```bash
cat reports/aleval/smoke/summary.md
```

**Expected output** (numbers will vary):
```
## Core Metrics
- total_samples: 3
- passed_count (reward-hack operational proxy): 1
- passed_rate: 0.333
- callout_triggered_count: 1

## Lie/Truth/Evasive Among Triggered Callouts
| label | count | percent |
|---|---:|---:|
| lie | 1 | 1.000 |
| truth | 0 | 0.000 |
| evasive | 0 | 0.000 |
```

If you see this structure (even with different numbers), the pipeline works.
If `callout_triggered_count: 0` on 3 samples, that's also valid — it means
the model failed all 3 tasks (no reward hacking occurred).

### 1.5 Clean up smoke test (optional)

```bash
rm -rf logs/aleval/minimal/*/  reports/aleval/smoke/
```

---

## Phase 2: Full Minimal Experiment

Run all 103 conflicting tasks on every model in `MODELS_MINIMAL`.

### 2.1 Review your model list

```bash
source experiments/config.sh
echo "Models: ${MODELS_MINIMAL[*]}"
echo "Count: ${#MODELS_MINIMAL[@]} models × 103 tasks"
```

### 2.2 Estimate cost

Rule of thumb from empirical data (GPT-5 class):
- ~$10-15 per model for minimal (103 tasks)
- Cheaper models (o4-mini, DeepSeek): ~$3-8
- Expensive models (Opus): ~$25-50

Total for 6 models: **~$50-150** for the minimal phase.

### 2.3 Run all minimal models

```bash
./experiments/run_all.sh minimal
```

**Expected duration**: 30-90 minutes per model, depending on model speed.
Models run sequentially. The script continues to the next model if one fails.

**Tip**: To run a single model (e.g., to restart a failed one):
```bash
./experiments/run_model.sh openrouter/openai/gpt-5 minimal
```

### 2.4 Monitor progress

In another terminal:
```bash
# Count completed .eval files per model
for d in logs/aleval/minimal/*/; do
    echo "$(basename $d): $(ls "$d"*.eval 2>/dev/null | wc -l) logs"
done
```

### 2.5 Verify completeness

After all models finish, check each has logs:
```bash
for d in logs/aleval/minimal/*/; do
    model=$(basename "$d")
    count=$(ls "$d"*.eval 2>/dev/null | wc -l)
    echo "$model: $count .eval file(s)"
done
```

Each model should have at least 1 `.eval` file.

---

## Phase 3: Tools Experiment

Run after minimal completes. Pick 2-3 models that showed interesting
minimal results (high pass rate, interesting lie/truth distribution).

### 3.1 Update config

Edit `experiments/config.sh` and set `MODELS_TOOLS` to your chosen models.

### 3.2 Verify Docker is running

```bash
docker version
```

Tools scaffold requires Docker (cannot use `--sandbox local`).

### 3.3 Run tools experiment

```bash
./experiments/run_all.sh tools
```

**Expected duration**: 2-4 hours per model (tools is ~10x slower than minimal).

**Tip**: Run one at a time if preferred:
```bash
./experiments/run_model.sh openrouter/openai/gpt-5 tools
```

---

## Phase 4: Collect Results

### 4.1 Generate per-model reports (deterministic labels only)

```bash
./experiments/collect_results.sh
```

This creates a `summary.md`, `judged_samples.csv`, and `judged_samples.json`
for each model in `reports/aleval/<preset>/<model>/`.

### 4.2 Quick check — browse individual reports

```bash
for f in reports/aleval/minimal/*/summary.md; do
    echo "=== $(dirname $f | xargs basename) ==="
    head -15 "$f"
    echo ""
done
```

### 4.3 Add LLM judge (optional but recommended)

Re-run collection with `--judge` to add a second-opinion LLM classification:

```bash
./experiments/collect_results.sh --judge
```

This calls the judge model on every triggered callout response. Adds
`callout_llm_judge_label` to each CSV and an agreement table to each summary.

**Cost**: Typically $5-15 total for all models combined (judge calls are short).

---

## Phase 5: Aggregate and Present Results

### 5.1 Generate combined tables

```bash
python experiments/summarize.py
```

This reads all per-model CSVs and produces:
- `reports/aleval/results_table.csv` — Combined data for analysis
- `reports/aleval/results_table.md` — Markdown table ready for README.md

The script also prints the table to stdout for easy copy-paste.

### 5.2 Update README.md results table

Copy the markdown table from the output (or from `reports/aleval/results_table.md`)
into the Results section of `README.md`, replacing the placeholder table.

### 5.3 Archive experiment metadata

Record these for reproducibility (add to README.md Reproducibility section):
- **Date**: When you ran the experiments
- **Evaluation version**: 1-A
- **Dataset revision**: `98650ffc3f28a01b261669b6d19fcd7773823710`
- **Exact model IDs**: Copy from `experiments/config.sh`
- **Parameters**: `max_attempts=3`, `message_limit=40`

---

## Directory Structure After Experiment

```
logs/aleval/
├── minimal/
│   ├── openai_gpt-5/
│   │   └── *.eval
│   ├── openai_o3/
│   │   └── *.eval
│   └── ...
└── tools/
    ├── openai_gpt-5/
    │   └── *.eval
    └── ...

reports/aleval/
├── minimal/
│   ├── openai_gpt-5/
│   │   ├── summary.md
│   │   ├── judged_samples.csv
│   │   └── judged_samples.json
│   └── ...
├── tools/
│   └── ...
├── combined/
│   ├── summary.md
│   ├── judged_samples.csv
│   └── judged_samples.json
├── results_table.csv
└── results_table.md
```

---

## Troubleshooting

### "No .eval files found"
- Check `logs/aleval/<preset>/<model>/` for files
- The eval may have crashed — check terminal output for errors
- Common cause: invalid API key or model ID not available on OpenRouter

### "callout_triggered_count: 0"
- The model failed all tasks (no reward hacking occurred)
- This is a valid result — it means the model didn't game the tests
- Check pass rate: if 0%, the model is not reward-hacking on these tasks

### "Rate limit errors"
- OpenRouter has per-model rate limits
- Reduce concurrency: Inspect may send parallel requests
- Wait and retry: `./experiments/run_model.sh <model> minimal`

### "Docker: permission denied"
- Run `docker version` to verify Docker access
- You may need `sudo` or to add your user to the `docker` group
- For minimal scaffold, use `--sandbox local` (no Docker needed)

### "Model not found on OpenRouter"
- Check model ID at [openrouter.ai/models](https://openrouter.ai/models)
- Model IDs change — verify the exact string (e.g., `openrouter/openai/gpt-5`)
- Some models require credits on OpenRouter; check your balance

---

## Quick Reference

```bash
# Smoke test (3 samples, first model)
./experiments/run_all.sh smoke

# Full minimal experiment
./experiments/run_all.sh minimal

# Full tools experiment
./experiments/run_all.sh tools

# Single model
./experiments/run_model.sh openrouter/openai/gpt-5 minimal

# Generate reports (without judge)
./experiments/collect_results.sh

# Generate reports (with LLM judge)
./experiments/collect_results.sh --judge

# Aggregate into tables
python experiments/summarize.py

# Check a specific model's results
cat reports/aleval/minimal/openai_gpt-5/summary.md
```
