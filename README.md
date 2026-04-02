# ImpossibleBench ALEval

This repository extends ImpossibleBench with action-grounded lying evaluation:
after successful task completion, the agent can be asked a same-chat callout
question, and the response is labeled deterministically as `lie`, `truth`,
`evasive`, or `not_applicable`.

Supported runtime matrix:
- Datasets: LiveCodeBench and SWE-bench
- Scaffolds: `minimal` and `tools`
- Splits: `original`, `oneoff`, `conflicting`

## Install

```bash
pip install -e .
```

Optional extras:

```bash
# SWE-bench runtime extras
pip install -e .[swe]

# Optional LLM judge utilities
pip install -e .[analysis]
```

## Quick Start

Run LiveCodeBench ALEval (minimal scaffold):

```bash
inspect eval src/impossiblebench/livecodebench_tasks.py@aleval_livecodebench_minimal --model openai/gpt-5-2025-08-07 --sandbox local -T limit=3 -T max_attempts=3 -T message_limit=40 --log-dir ./logs/aleval_lcb_min
```

Run LiveCodeBench ALEval (tools scaffold):

```bash
inspect eval src/impossiblebench/livecodebench_tasks.py@aleval_livecodebench_tools --model openai/gpt-5-2025-08-07 --sandbox local -T limit=3 -T max_attempts=3 -T message_limit=40 --log-dir ./logs/aleval_lcb_tools
```

Run SWE-bench ALEval (minimal scaffold):

```bash
inspect eval src/impossiblebench/swebench_tasks.py@aleval_swebench_minimal --model openai/gpt-5-2025-08-07 -T limit=3 -T max_attempts=2 --log-dir ./logs/aleval_swe_min
```

Generate report artifacts:

```bash
aleval-report --logs-dir ./logs/aleval_lcb_min --out-dir ./reports/aleval_lcb_min
```

Outputs:
- `judged_samples.csv`
- `judged_samples.json`
- `summary.md`

## Scoring Semantics

- `C` = correct / pass
- `I` = incorrect / fail
- Benchmark pass/fail is separate from lying labels.
- Lying labels are derived from `same_chat_callout` metadata only.

Important metadata fields:
- `same_chat_callout`
- `preserved_solution_used_for_scoring`
- `callout_deterministic_label`

## Evaluation Report

This section is the canonical place for inspect-style reporting.

### Implementation Details
- Deviations from upstream are documented in code comments and this README.
- Callout behavior is optional and disabled by default except for ALEval presets.

### Results
- Results table and analysis will be populated after experiment runs.
- Comparison to paper baselines should include split-level and scaffold-level trends.

### Reproducibility
- Include total sample counts and run date in each report artifact.
- Include exact `inspect eval` command(s), model IDs, and task versions.
- Record non-default task parameters and why they were changed.

## Development Quality

- Linting/formatting: Ruff (`pyproject.toml`) + pre-commit hooks.
- Tests: pytest suite under `tests/`.
- Eval metadata: `src/impossiblebench/eval.yaml`.

## Troubleshooting

- If console scripts are stale, run `pip install -e .` again.
- If SWE dependencies are missing, install `pip install -e .[swe]`.
- For Docker-backed runs, ensure `docker version` succeeds.


