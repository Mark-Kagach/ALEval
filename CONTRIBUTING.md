# Contributing to ALEval

## Getting Started

```bash
git clone https://github.com/fjzzq2002/impossiblebench.git
cd impossiblebench
pip install -e ".[dev,test]"
pre-commit install
```

## Development Workflow

1. Create a branch from `main`
2. Make your changes
3. Run lint and tests:
   ```bash
   make lint    # or: ruff check src/ tests/ && ruff format --check src/ tests/
   make test    # or: pytest tests/ -v -m "not docker and not slow"
   ```
4. Commit with a descriptive message
5. Open a pull request against `main`

## Testing

```bash
# Fast unit tests only
pytest tests/unit/ -v

# All tests except Docker-dependent
pytest tests/ -v -m "not docker and not slow"

# Full test suite (requires Docker)
pytest tests/ -v
```

### Test markers

| Marker | Meaning |
|--------|---------|
| `@pytest.mark.slow` | Takes >10s |
| `@pytest.mark.docker` | Requires Docker |
| `@pytest.mark.dataset_download` | Downloads from HuggingFace |
| `@pytest.mark.huggingface` | Calls HuggingFace APIs |

### Writing tests

- Unit tests go in `tests/unit/`, integration tests in `tests/integration/`
- Use fixtures from `tests/conftest.py`: `FakeTaskState`, `FakeOutput`, `make_fake_generate()`
- Mock external calls (sandbox, model API) in unit and integration tests
- Mark any test requiring Docker or network with the appropriate marker

## Code Style

- **Formatter/Linter**: [Ruff](https://docs.astral.sh/ruff/) (configured in `pyproject.toml`)
- **Line length**: 100 characters
- **Python version**: 3.10+ (use `from __future__ import annotations` for modern type syntax)
- **Imports**: Sorted by ruff's isort with `impossiblebench` as first-party

Run before committing:
```bash
ruff check --fix src/ tests/
ruff format src/ tests/
```

## Submitting Evaluation Results

To contribute results from running ALEval on a model:

1. Run the full eval with a known model and record the exact command:
   ```bash
   inspect eval src/impossiblebench/lcb/tasks.py@aleval_livecodebench_minimal \
     --model openrouter/<provider>/<model> \
     --sandbox local \
     --log-dir ./logs/aleval
   ```
2. Generate the report:
   ```bash
   aleval-report --logs-dir ./logs/aleval --out-dir ./reports/aleval
   ```
3. Add a row to the Results table in `README.md` with: model name, preset, sample count, pass rate, lie/truth/evasive rates
4. Include the exact `inspect eval` command and model version in your PR description

## Reporting Issues

When filing an issue, include:
- Python version (`python --version`)
- The exact command you ran
- Full error traceback
- OS and Docker version (if relevant)
