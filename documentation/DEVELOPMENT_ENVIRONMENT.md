# Development environment: Windows vs WSL

ALEval currently exists in two places on this machine:

- `C:\Users\thepe\OneDrive\Desktop\ALEval`
- `~/work/ALEval` inside WSL

To keep experiments, code, and GitHub aligned, the **single source of truth** should be the **WSL repo** at `~/work/ALEval`.

## Short answer

- Run experiments from `~/work/ALEval`.
- Edit the repo at `~/work/ALEval`.
- Commit and push from `~/work/ALEval`.
- Treat the Windows checkout as a secondary copy, not the canonical repo.

If you want one folder to use everywhere, open the WSL repo directly from Windows tools:

```text
\\wsl.localhost\Ubuntu\home\mk\work\ALEval
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
- the WSL virtualenv at `~/work/ALEval/.venv`
- logs written under `~/work/ALEval/logs/...`

It does **not** automatically use newer edits sitting in the Windows checkout.

## Recommended workflow

1. Open `\\wsl.localhost\Ubuntu\home\mk\work\ALEval` in Cursor.
2. Use a WSL terminal:

   ```bash
   cd ~/work/ALEval
   source .venv/bin/activate
   ```

3. Before a run:

   ```bash
   git pull
   pip install -e ".[test,analysis]"
   python scripts/print_core_versions.py
   ```

4. Run experiments from that same shell.
5. Commit and push from that same repo so GitHub matches the code you actually ran.

Add `,swe` if you need SWE-bench:

```bash
pip install -e ".[test,analysis,swe]"
```

## GitHub relationship

GitHub only reflects **committed and pushed** files.

- `src/`, `README.md`, `pyproject.toml`, `documentation/`, and `scripts/` belong in git.
- `logs/` and `reports/` are intentionally gitignored local artifacts.
- Virtual environments are local only and are never the source of truth for code.

If a refactor exists only in a local working tree and is not committed, GitHub does not have it yet.

## Windows vs WSL environments

Python environments are not interchangeable:

- WSL venvs have Linux binaries and must be used from WSL.
- Windows venvs have Windows binaries and must be used from PowerShell / cmd.

For ALEval, the preferred runtime is the WSL env:

```bash
cd ~/work/ALEval
source .venv/bin/activate
```

You can still create a Windows venv for quick inspection work, but it should not be your primary experiment environment.

## Version check

After reinstalling, use:

```bash
python scripts/print_core_versions.py
```

The important checks are:

- `inspect_ai` resolves to the expected installed version
- `impossiblebench` resolves from the repo you are in

For the WSL workflow, `impossiblebench` should resolve from `~/work/ALEval/src/impossiblebench/...`.

## Storage layout

- **Code and docs:** tracked in git
- **Eval logs:** `logs/` and kept locally
- **Reports:** `reports/` and kept locally
- **GitHub repo:** only the committed subset of tracked files

Refactors live in git history, not in the virtualenv.

## Optional: `requirements.txt`

[`requirements.txt`](../requirements.txt) is a loose mirror of the core dependency floor. The authoritative install remains:

```bash
pip install -e ".[test,analysis]"
```
