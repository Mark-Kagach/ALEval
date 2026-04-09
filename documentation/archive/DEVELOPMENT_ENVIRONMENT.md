# Development Environment

## Setup

```bash
cd ~/work/ALEval
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test,analysis]"
```

Add `,swe` if you need SWE-bench Docker sandboxes:

```bash
pip install -e ".[test,analysis,swe]"
```

## Which code does `inspect eval` use?

`inspect eval src/...` uses the files in the **current working tree** that you launch it from.

Example:

```bash
cd ~/work/ALEval
source .venv/bin/activate
inspect eval src/impossiblebench/swe/tasks.py@aleval_swebench_minimal ...
```

That run uses:

- code from `~/work/ALEval/src/...`
- the virtualenv at `~/work/ALEval/.venv`
- logs written under `~/work/ALEval/logs/...`

## Storage layout

- **Code and docs:** tracked in git
- **Eval logs:** `logs/` (gitignored, kept locally)
- **Reports:** `reports/` (gitignored, kept locally)

## Version check

After reinstalling, verify:

```bash
python -c "import inspect_ai; print(inspect_ai.__version__)"
python -c "import impossiblebench; print(impossiblebench.__file__)"
```

- `inspect_ai` should resolve to the expected installed version
- `impossiblebench` should resolve from the repo's `src/impossiblebench/`
