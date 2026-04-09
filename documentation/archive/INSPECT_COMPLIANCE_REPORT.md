# Inspect Evals Compliance Report — ALEval

> What must change for this benchmark to pass the Inspect Evals contribution
> pipeline?

This report audits every source and test file against the actual requirements
from:

- [`EVALUATION_CHECKLIST.md`](https://github.com/UKGovernmentBEIS/inspect_evals/blob/main/EVALUATION_CHECKLIST.md)
- [`CONTRIBUTING.md`](https://github.com/UKGovernmentBEIS/inspect_evals/blob/main/CONTRIBUTING.md)
- [`BEST_PRACTICES.md`](https://github.com/UKGovernmentBEIS/inspect_evals/blob/main/BEST_PRACTICES.md)
- [`TASK_VERSIONING.md`](https://github.com/UKGovernmentBEIS/inspect_evals/blob/main/TASK_VERSIONING.md)
- [`.pre-commit-config.yaml`](https://github.com/UKGovernmentBEIS/inspect_evals/blob/main/.pre-commit-config.yaml)
- [`.github/workflows/checks.yml`](https://github.com/UKGovernmentBEIS/inspect_evals/blob/main/.github/workflows/checks.yml)
- [Ruff documentation](https://docs.astral.sh/ruff/)

Every item is graded **PASS**, **PARTIAL**, or **FAIL** with file-level evidence
and a concrete description of the required change.

---

## Table of Contents

1. [Packaging & Tooling](#1-packaging--tooling)
2. [Ruff Linting & Formatting](#2-ruff-linting--formatting)
3. [Import Style](#3-import-style)
4. [Type Hints](#4-type-hints)
5. [Docstrings](#5-docstrings)
6. [Task Construction](#6-task-construction)
7. [Dataset Version Pinning](#7-dataset-version-pinning)
8. [Prompt Templates](#8-prompt-templates)
9. [Error Handling](#9-error-handling)
10. [Scoring & Metrics](#10-scoring--metrics)
11. [eval.yaml Metadata](#11-evalyaml-metadata)
12. [Task Versioning](#12-task-versioning)
13. [Testing — Unit Tests](#13-testing--unit-tests)
14. [Testing — End-to-End Tests](#14-testing--end-to-end-tests)
15. [Testing — Pytest Marks](#15-testing--pytest-marks)
16. [Testing — conftest & Shared Utils](#16-testing--conftest--shared-utils)
17. [NOTICE File & Attribution](#17-notice-file--attribution)
18. [README & Evaluation Report](#18-readme--evaluation-report)
19. [Pre-commit Hooks](#19-pre-commit-hooks)
20. [CI Workflows](#20-ci-workflows)
21. [Evaluation Artifacts](#21-evaluation-artifacts)
22. [Evaluation Validity](#22-evaluation-validity)
23. [Miscellaneous Code Quality](#23-miscellaneous-code-quality)
24. [Summary Matrix](#24-summary-matrix)

---

## 1. Packaging & Tooling

**Status: FAIL**

### Requirement

Inspect Evals uses `uv` as its package manager with `pyproject.toml` for all
metadata. The CI runs `uv sync --frozen`, `uv run ruff check`, `uv run mypy`,
etc. There is no `setup.py` anywhere in the inspect_evals repo.

### Current State

- The project uses a legacy `setup.py` (65 lines) with `setuptools`.
- `pyproject.toml` exists but contains only `[build-system]`, `[tool.ruff]`,
  and `[tool.pytest.ini_options]` — no `[project]` table.
- No `uv.lock` file.
- No dev/test dependency groups.
- Dependencies specified via `install_requires` and `extras_require` in
  `setup.py`.

### Required Changes

1. **Delete `setup.py`**. Migrate all metadata to `pyproject.toml` under the
   `[project]` table:

   ```toml
   [project]
   name = "impossiblebench"
   version = "0.1.0"
   requires-python = ">=3.10"
   dependencies = [
       "inspect_ai>=0.3.0",
       "pandas>=2.0.0",
       # ...
   ]

   [project.optional-dependencies]
   swe = ["swebench>=4.0.0"]
   analysis = ["litellm>=1.50.0"]
   test = ["pytest", "pytest-asyncio", "pytest-dotenv"]

   [project.scripts]
   aleval-report = "impossiblebench.report.cli:main"
   ```

2. **Generate `uv.lock`** via `uv lock`.

3. **Add dependency groups** for dev/test:

   ```toml
   [dependency-groups]
   dev = ["ruff", "mypy", "pre-commit"]
   test = ["pytest>=8.0", "pytest-asyncio", "pytest-dotenv"]
   ```

4. **Update README** install commands from `pip install -e .` to
   `uv sync --group dev`.

---

## 2. Ruff Linting & Formatting

**Status: FAIL**

### Requirement

The inspect_evals CI runs `ruff check` and `ruff format --check` on every PR.
The pre-commit config pins Ruff v0.13.2. All files must pass both with zero
errors.

### Current State

Running `ruff check src/impossiblebench/ --select E,F,I,B,UP,W`:

| Rule | Violations |
|------|-----------|
| W293 (blank-line-with-whitespace) | 250 |
| E501 (line-too-long) | 166 |
| UP006 (non-pep585-annotation) | 113 |
| F401 (unused-import) | 55 |
| UP045 (non-pep604-annotation-optional) | 31 |
| I001 (unsorted-imports) | 29 |
| F541 (f-string-missing-placeholders) | 27 |
| W291 (trailing-whitespace) | 17 |
| UP035 (deprecated-import) | 12 |
| F841 (unused-variable) | 11 |
| E722 (bare-except) | 6 |
| W292 (missing-newline-at-end-of-file) | 6 |
| Other (B007, B904, B011, E401, E402, E731, E741, F811, UP007, UP015) | 19 |
| **TOTAL** | **744** |

Running `ruff format --check src/impossiblebench/`: **31 of 34 files** would be
reformatted.

Running `ruff check tests/`: **31 additional errors** (unsorted imports, unused
imports, line-too-long, `== True` comparisons).

### Required Changes

1. **Run `ruff check --fix src/ tests/`** to auto-fix the ~492 fixable
   violations (import sorting, whitespace, deprecated types, f-strings).

2. **Manually fix** the ~252 non-auto-fixable violations:
   - 166 lines over 100 characters — break them
   - 11 unused variables — remove or prefix with `_`
   - 6 bare `except:` clauses — specify exception types
   - 3 `raise` without `from` inside `except` — add `from e` or `from None`
   - 2 `assert False` — replace with `raise AssertionError`
   - 1 lambda assignment — convert to `def`
   - 1 invalid syntax — fix the file

3. **Run `ruff format src/ tests/`** to reformat all 31+3 files.

4. **Add Ruff rule sets** to match inspect_evals. Their pyproject.toml extends
   beyond E/F/I/B/UP to also include W (whitespace). Consider enabling the
   same set. At minimum, the existing `select = ["E", "F", "I", "B", "UP"]`
   should also include `"W"`.

5. **Pin ruff version** in pyproject.toml to match pre-commit config:

   ```toml
   [tool.ruff]
   required-version = ">=0.13.2"
   ```

6. **Tests must also pass ruff** — currently 31 errors.

---

## 3. Import Style

**Status: FAIL**

### Requirement

From CONTRIBUTING.md: *"Use absolute imports instead of relative imports."*

From BEST_PRACTICES.md: *"Prefer absolute package imports
(e.g., `from inspect_evals.your_eval.dataset import get_dataset` instead of
`from .dataset import get_dataset`) so modules/tests run from IDEs and plugins
that execute from arbitrary working directories."*

### Current State

40+ relative imports across 10 files:

| File | Relative Import Count |
|------|----------------------|
| `src/impossiblebench/__init__.py` | 8 |
| `src/impossiblebench/lcb/__init__.py` | 4 |
| `src/impossiblebench/lcb/tasks.py` | 6 |
| `src/impossiblebench/lcb/solver_minimal.py` | 2 |
| `src/impossiblebench/swe/__init__.py` | 5 |
| `src/impossiblebench/swe/tasks.py` | 8 |
| `src/impossiblebench/swe/solver_tools.py` | 1 |
| `src/impossiblebench/swe/solver_minimal.py` | 2 |
| `src/impossiblebench/report/__init__.py` | 2 |
| `src/impossiblebench/report/cli.py` | 2 |

### Required Changes

Convert every `from .module import X` to
`from impossiblebench.subpackage.module import X`. For example:

```python
# Before (lcb/tasks.py)
from .solver_minimal import agentic_humaneval_solver
from .scorers import agentic_humaneval_scorer

# After
from impossiblebench.lcb.solver_minimal import agentic_humaneval_solver
from impossiblebench.lcb.scorers import agentic_humaneval_scorer
```

Every relative import in every file listed above must be converted. The
backward-compatible re-export stubs (`livecodebench_tasks.py`, etc.) already
use absolute imports and need no change.

---

## 4. Type Hints

**Status: FAIL**

### Requirement

From CONTRIBUTING.md: *"Include type hints for all functions."*

From BEST_PRACTICES.md: *"Don't add type annotations outside of function
arguments when they're redundant."*

The CI runs **mypy** across Python 3.11, 3.12, and 3.13.

### Current State

Functions missing return type annotations (representative, not exhaustive):

| File | Function | Missing |
|------|----------|---------|
| `callout.py` | `same_chat_callout_solver()` | Return type `Solver` |
| `callout.py` | `solve()` (inner) | `generate` param type |
| `lcb/tasks.py` | `eval_set` fallback | All annotations |
| `lcb/solver_minimal.py` | `solve()` outer factory | Return type |
| `lcb/solver_tools.py` | `custom_incorrect_message()`, `init()`, `run()` | All annotations |
| `swe/tasks.py` | `eval_set` fallback | All annotations |
| `swe/solver_minimal.py` | `mini_agent_solver()` | `-> Solver` return |
| `swe/solver_tools.py` | `custom_incorrect_message()`, `init()`, `run()` | All annotations |
| `report/cli.py` | `compute_summary()` | Parameter types, return |
| `report/data_loader.py` | `get_dump_of_everything()` | All annotations |
| `report/llm_judge.py` | `_evaluate_pair()`, `evaluate_func_with_index()` | Return type |

Additionally, many functions use `typing.Optional[X]` / `typing.List[X]` /
`typing.Dict[X, Y]` instead of the PEP 604/585 equivalents (`X | None`,
`list[X]`, `dict[X, Y]`) that ruff flags under UP006/UP045.

### Required Changes

1. **Add return type annotations** to every public and private function.
   Inner closures within `@solver`/`@scorer` should annotate at least the
   return type.

2. **Convert all `Optional[X]`** to `X | None` (PEP 604).

3. **Convert all `List[X]`, `Dict[X, Y]`, `Tuple[X, ...]`** to `list[x]`,
   `dict[x, y]`, `tuple[x, ...]` (PEP 585).

4. **Add a mypy configuration** to `pyproject.toml`:

   ```toml
   [tool.mypy]
   python_version = "3.10"
   warn_return_any = true
   warn_unused_configs = true
   ```

5. **Fix all mypy errors** until `mypy .` passes clean.

---

## 5. Docstrings

**Status: PARTIAL**

### Requirement

From CONTRIBUTING.md: *"Add docstrings following Google style guide."* and
*"Write the code to be read by other developers with no prior knowledge of the
eval — it should be possible to understand the code without reading the paper."*

### Current State

Many functions have docstrings, but the format is inconsistent:

- **Good**: `impossible_livecodebench()` in `lcb/tasks.py`,
  `mini_agent_solver()` in `swe/solver_minimal.py`, and most of
  `report/llm_judge.py` have `Args:` sections.
- **Missing `Returns:` / `Raises:`**: Even the good docstrings rarely include
  `Returns:` or `Raises:` sections.
- **No docstrings**: `callout.py` functions have single-line descriptions
  without `Args:`/`Returns:`. `lcb/scorers.py` factory functions and
  `swe/scorers.py` functions mostly have one-paragraph docstrings.

### Required Changes

1. **Every public function** must have a Google-style docstring:

   ```python
   def classify_callout_response(response: str) -> str:
       """Classify a callout response as yes/no/evasive using regex.

       Args:
           response: The raw text response from the agent.

       Returns:
           One of "yes", "no", or "evasive".
       """
   ```

2. **Every `@task`, `@solver`, `@scorer` function** must have a docstring
   explaining what it does, its parameters, and its return.

3. **Module-level docstrings** should be added to every `.py` file describing
   the module's purpose. Some files have them; many don't.

---

## 6. Task Construction

**Status: FAIL**

### Requirement

From CONTRIBUTING.md: *"Do not pass a `name` parameter to the task — this is
only used for dynamically created tasks (i.e. tasks that are not addressable on
the filesystem or in a package)."*

From BEST_PRACTICES.md: *"Differentiate tasks from dataset splits via
parameters."* and *"Provide defaults and allow overrides for datasets, solvers,
scorers, metrics, and grader models."*

### Current State

Both task files explicitly construct and pass `name=` to `Task()`:

```python
# lcb/tasks.py:97
task_name = f"lcb_{split}"
# ...
return Task(name=task_name, ...)

# swe/tasks.py:298-316
task_name = f"swebench_{split}"
# ...
return Task(name=task_name, ...)
```

Additionally, the `aleval_*` preset functions create named presets like
`aleval_livecodebench_minimal` — these ARE addressable by filesystem/package
path via `inspect eval`, so they should not set `name=`.

### Required Changes

1. **Remove `name=task_name`** from all `Task()` calls in `lcb/tasks.py` and
   `swe/tasks.py`. Let Inspect derive the name from the `@task` function name.

2. **Verify tasks are invocable** via:
   ```bash
   inspect eval impossiblebench/lcb/tasks.py@aleval_livecodebench_minimal
   ```

3. If dynamic naming is truly needed for some variant construction, document
   why it's an exception and add a ruff suppression comment.

---

## 7. Dataset Version Pinning

**Status: FAIL**

### Requirement

From EVALUATION_CHECKLIST.md: *"Datasets are pinned to specific versions: all
HuggingFace loading functions (`hf_dataset`, `load_dataset`,
`snapshot_download`, `hf_hub_download`) enforce `revision=` at runtime, and
GitHub raw URLs use commit SHAs instead of branch names."*

From BEST_PRACTICES.md: *"Pin HuggingFace datasets by passing `revision=<sha>`
to `hf_dataset()` or `load_dataset()` calls."*

### Current State

```python
# lcb/tasks.py:44
LCB_DATASET_REVISION = None

# swe/tasks.py:52
SWEBENCH_DATASET_REVISION = None
```

Both datasets are loaded with `revision=None`, meaning the latest version on
HuggingFace is used at eval time. Results are non-reproducible if the upstream
data changes.

### Required Changes

1. **Look up the current commit SHA** for each dataset:
   - `fjzzq2002/impossible_livecodebench` on HuggingFace
   - `fjzzq2002/impossible_swebench` on HuggingFace

2. **Pin them as constants**:

   ```python
   LCB_DATASET_REVISION = "abc123def456..."   # Pinned 2026-04-04
   SWEBENCH_DATASET_REVISION = "789abc012..."  # Pinned 2026-04-04
   ```

3. **Also define the dataset path as a module constant** (per CONTRIBUTING.md):

   ```python
   LCB_DATASET_PATH = "fjzzq2002/impossible_livecodebench"
   ```

4. **Document the pinned versions** in the README.

---

## 8. Prompt Templates

**Status: PARTIAL**

### Requirement

From BEST_PRACTICES.md: *"Separate prompt templates from formatting. Keep
prompt text as module-level constants and inject variables at call time."*

### Current State

Mixed compliance:

| File | Status |
|------|--------|
| `callout.py` | **PASS** — `DEFAULT_CALLOUT_PROMPT` is module constant |
| `lcb/tasks.py` | **PASS** — `INSTRUCTION`, `INSTRUCTION_SUFFIX`, `INSTRUCTION_SUFFIX_TOOLS` are constants |
| `swe/solver_minimal.py` | **PASS** — `MINI_AGENT_SYSTEM_TEMPLATE`, `MINI_AGENT_INSTANCE_TEMPLATE`, etc. are constants |
| `report/llm_judge.py` | **PASS** — `BINARY_PROMPT`, `CLASSIFY_PROMPT`, `LIE_PROMPT` are constants |
| `swe/tasks.py` | **PASS** — `DEFAULT_INPUT_PROMPT` is constant |
| `lcb/solver_tools.py` | **FAIL** — large system prompt in `custom_init_message` is an inline `dedent(f"""...""")` |
| `swe/solver_tools.py` | **FAIL** — `tool_setup` inline; main template from `_get_default_template()` function |
| `swe/scorers.py` | **FAIL** — `CREATE_MODEL_PATCH`, bash eval script built inline with `dedent(f"""...""")` |
| `lcb/tasks.py` `__main__` | **FAIL** — long inline `instruction_prompt` string in `__main__` block |

### Required Changes

1. **Extract inline prompts** in `lcb/solver_tools.py`,
   `swe/solver_tools.py`, and `swe/scorers.py` into module-level constants
   with `ALL_CAPS` names.

2. **Use `.format()` or f-strings** at call time for variable injection.

3. **Remove `__main__` blocks** (see [Section 23](#23-miscellaneous-code-quality))
   or move their prompts to constants.

---

## 9. Error Handling

**Status: FAIL**

### Requirement

From BEST_PRACTICES.md: *"Only handle errors gracefully if you have a clear,
justified reason. Otherwise, let them raise and crash. Failing fast is better
than silently running broken code. Do not write try catch blocks unless it
absolutely makes sense."*

### Current State

Bare `except:` and broad `except Exception:` blocks are endemic:

| File | Bare `except:` | `except Exception:` |
|------|----------------|---------------------|
| `report/llm_judge.py` | 1 (line ~935) | 10+ |
| `lcb/scorers.py` | 1 (line ~276) | 4 |
| `report/data_loader.py` | 1 (line ~293) | 2 |
| `swe/scorers.py` | 2 (lines ~118, ~122) | 0 |
| `swe/solver_minimal.py` | 1 (line ~661) | 3 |
| `lcb/solver_tools.py` | 0 | 1 |
| `swe/solver_tools.py` | 0 | 1 |
| `swe/build_images.py` | 0 | 1 |
| `lcb/solver_minimal.py` | 0 | 1 |

The `except Exception: pass` in `swe/solver_tools.py:276` is particularly
concerning — it silently swallows all exceptions during the scorer verification
step, meaning a broken scorer would cause the callout to silently not fire.

### Required Changes

1. **Remove all bare `except:` clauses** — specify the exception type.

2. **Audit every `except Exception:`** — for each one, either:
   - Narrow it to the specific exception expected (e.g.,
     `except FileNotFoundError:`, `except json.JSONDecodeError:`), or
   - Let it propagate (remove the try/except entirely), or
   - If suppression is intentional, add a comment explaining why, and at
     minimum log the exception.

3. **Add `from e` or `from None`** to all `raise` inside `except` blocks
   (ruff B904).

4. **The `swe/solver_tools.py:276` `except Exception: pass`** must be
   converted to at minimum log the error, or better, propagate it.

---

## 10. Scoring & Metrics

**Status: PARTIAL**

### Requirement

From BEST_PRACTICES.md:
- *"Align scoring with the outcome."*
- *"Use [accuracy(), stderr()] as a minimal set of metrics for binary outcomes."*
- *"Avoid magic values; use framework constants — compare against
  `CORRECT`/`INCORRECT`."*
- *"Record important run metadata."*
- *"Avoid storing reducible score values in Score.metadata."*

From EVALUATION_CHECKLIST.md (Scoring Validity):
- *"The scorer measures actual task completion rather than a proxy for it."*
- *"Substring matching is only used when the matched text is itself the ground
  truth."*

### Current State

- Scorers use literal `1.0` / `0.0` as score values rather than Inspect's
  `CORRECT`/`INCORRECT` constants.
- The callout classifier (`classify_callout_response`) uses regex matching on
  natural language — exactly the pattern the guidelines warn against.
- The `callout_deterministic_label` is stored in `Score.metadata`, which means
  it will **not** be properly reduced across epochs.
- No explicit `metrics=[accuracy(), stderr()]` on task definitions (relies on
  defaults).

### Required Changes

1. **Use `CORRECT`/`INCORRECT` constants** from `inspect_ai.scorer` instead of
   literal `1.0`/`0.0`.

2. **Document the regex classifier's limitations** clearly and provide a
   meta-validation (per Task Validity: *"LLM-as-a-judge evals must provide a
   meta-eval where the judge's consistency and resistance to adversarial outputs
   are tested"*). Since ALEval has both a regex and LLM judge, both need
   validation.

3. **Move `callout_deterministic_label`** into `Score.value` if it needs to be
   aggregated, or document that it's a per-sample identifier that should NOT be
   reduced.

4. **Explicitly set metrics** on task definitions:
   ```python
   Task(..., scorer=my_scorer(), metrics=[accuracy(), stderr()])
   ```

---

## 11. eval.yaml Metadata

**Status: FAIL**

### Requirement

Per CONTRIBUTING.md and the eval.yaml reference, every task must have accurate
`dataset_samples`, optional `dependency`, `version`, and appropriate `metadata`.

### Current State

```yaml
tasks:
  - name: aleval_livecodebench_minimal
    dataset_samples: 0
  - name: aleval_livecodebench_tools
    dataset_samples: 0
  - name: aleval_swebench_minimal
    dataset_samples: 0
  - name: aleval_swebench_tools
    dataset_samples: 0
```

- `dataset_samples: 0` for all four tasks.
- No `version` field.
- No `dependency` field.
- No `human_baseline`.

### Required Changes

1. **Set `dataset_samples`** to the actual count for each task. Run each task
   with `--limit 1` and note the total sample count reported.

2. **Add `version: "1-A"`** per TASK_VERSIONING.md.

3. **Add `dependency`** if the eval requires extras:
   ```yaml
   dependency: "impossiblebench"
   ```

4. **Add `human_baseline`** if available, or document its absence.

---

## 12. Task Versioning

**Status: FAIL**

### Requirement

From TASK_VERSIONING.md: *"The task `version` attribute must be set on every
task in inspect_evals."* Version must follow the `N-X` scheme (e.g., `1-A`).

### Current State

No `version` field in `eval.yaml`. No changelog section in README.

### Required Changes

1. **Set `version: "1-A"`** in `eval.yaml`.

2. **Add a Changelog section** to `README.md`:

   ```markdown
   ## Changelog

   ### v1-A (2026-04-04)
   - Initial implementation with LiveCodeBench and SWE-bench variants
   - Same-chat callout architecture
   - Deterministic + optional LLM judge classification
   ```

3. **Bump version** on future changes per the N-X scheme.

---

## 13. Testing — Unit Tests

**Status: PARTIAL**

### Requirement

From CONTRIBUTING.md: *"Include unit tests that cover all non-trivial custom
functions."* Including:
- Solver, scorer and dataset functions
- Custom tools
- Custom utils or functions
- Edge cases, error conditions, and invalid inputs
- A `record_to_sample` test with an actual dataset example

### Current State

The test suite has 61 passing + 2 xfailed tests covering:

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `unit/test_callout_classify.py` | 11 | `classify_callout_response` edge cases |
| `unit/test_callout_label.py` | 8 | `deterministic_callout_label` branches |
| `unit/test_callout_solver.py` | 6 | `same_chat_callout_solver` behavior |
| `unit/test_split_validation.py` | 4 | `validate_callout_split` |
| `unit/test_task_name_parser.py` | 4 | `parse_task_display_name` |
| `unit/test_find_code.py` | 6 | `find_code` extraction |
| `integration/test_scorer_metadata.py` | 4 | Scorer metadata attachment |
| `integration/test_report_pipeline.py` | 3 | Report generation |
| `integration/test_lcb_minimal_callout.py` | 3 | LCB minimal flow |
| `integration/test_lcb_tools_callout.py` | 2 | LCB tools flow |
| `integration/test_swe_minimal_callout.py` | 3 | SWE minimal flow |
| `integration/test_swe_tools_callout.py` | 2 | SWE tools flow |

**Gaps:**

- **No `record_to_sample` test** — there is no test demonstrating the dataset
  `record_to_sample` function with an actual HuggingFace record example. This
  is explicitly required.
- **No dataset structure validation** — should use
  `assert_huggingface_dataset_structure`.
- **No unit tests for `report/data_loader.py`** DataLoader — parsing of `.eval`
  files is untested at the unit level.
- **No unit tests for `report/llm_judge.py`** LLMJudge — the classifier
  prompts, retry logic, and response parsing are untested.
- **No unit tests for `swe/build_images.py`** — Docker image building logic.
- **No unit tests for `apply_patch.py`** — patch parsing/application logic.
- **No unit tests for `find_code` edge cases** around security
  (e.g., code injection in markdown blocks).

### Required Changes

1. **Add `record_to_sample` tests** for both LCB and SWE-bench datasets:

   ```python
   def test_lcb_record_to_sample():
       record = {
           "question_title": "Two Sum",
           "question_content": "Given an array...",
           "test": "assert solution([2,7,11,15], 9) == [0,1]",
           # ... all fields from actual dataset
       }
       sample = record_to_sample(record)
       assert sample.input == "Given an array..."
       assert sample.target == "assert solution([2,7,11,15], 9) == [0,1]"
   ```

2. **Add unit tests** for `DataLoader`, `LLMJudge`, `build_images`,
   and `apply_patch`.

3. **Add HuggingFace dataset structure validation** using
   `assert_huggingface_dataset_structure`.

---

## 14. Testing — End-to-End Tests

**Status: FAIL**

### Requirement

From CONTRIBUTING.md: *"It is also required that you implement at least one
end-to-end test for your evaluation. This should be a test that demonstrates
the full evaluation pipeline, including the solver and scorer. It should use
`mockllm/model` as the model."*

*"If your eval has multiple tasks or a task with multiple variants, you should
implement one success end-to-end test and one error handling end-to-end test
for each meaningfully different task/variant."*

### Current State

**Zero end-to-end tests using `mockllm/model`.** The existing "integration"
tests use hand-rolled `FakeTaskState`/`FakeOutput` mocks that bypass the
Inspect pipeline entirely. They never call `eval()`, never produce an eval log,
and never test the actual task → solver → scorer → metrics flow.

### Required Changes

1. **Create proper E2E tests** for each of the 4 ALEval presets. Each test
   must:

   ```python
   from inspect_ai import eval
   from inspect_ai.model import ModelOutput, get_model

   @pytest.mark.dataset_download
   @pytest.mark.huggingface
   def test_aleval_lcb_minimal_e2e_default_mock():
       [log] = eval(
           tasks=aleval_livecodebench_minimal(),
           limit=1,
           model="mockllm/model",
       )
       assert log.status == "success"
       assert log.results is not None
       scores = log.results.scores[0]
       assert "accuracy" in scores.metrics

   @pytest.mark.dataset_download
   @pytest.mark.huggingface
   def test_aleval_lcb_minimal_e2e_correct_mock():
       [log] = eval(
           tasks=aleval_livecodebench_minimal(),
           limit=1,
           model=get_model(
               "mockllm/model",
               custom_outputs=[
                   ModelOutput.from_content(
                       model="mockllm/model",
                       content="def solution(): pass",
                   ),
               ],
           ),
       )
       assert log.status == "success"
   ```

2. **For SWE-bench variants**, add Docker marks:

   ```python
   @pytest.mark.slow(120)
   @pytest.mark.docker
   @pytest.mark.dataset_download
   @pytest.mark.huggingface
   def test_aleval_swe_minimal_e2e():
       # ...
   ```

3. **Test the report pipeline E2E** — generate a mock eval log, then run
   `compute_summary` on it.

---

## 15. Testing — Pytest Marks

**Status: FAIL**

### Requirement

From EVALUATION_CHECKLIST.md:
- `@pytest.mark.dataset_download` if test triggers dataset download
- `@pytest.mark.huggingface` if test uses HuggingFace
- `@pytest.mark.docker` if test uses Docker sandbox
- `@pytest.mark.slow(N)` if test takes >10 seconds

### Current State

**Zero pytest marks** are applied across all test files. The markers are
*registered* in `pyproject.toml` but never *used*.

### Required Changes

1. **Mark every E2E test** that instantiates a dataset with
   `@pytest.mark.dataset_download`.

2. **Mark every test** that calls HuggingFace with `@pytest.mark.huggingface`.

3. **Mark every test** that uses Docker with `@pytest.mark.docker`.

4. **Mark any test** expected to take >10s with `@pytest.mark.slow(N)`.

5. **Add conftest.py skip logic** that respects these markers (see next
   section).

---

## 16. Testing — conftest & Shared Utils

**Status: FAIL**

### Requirement

The inspect_evals `conftest.py` provides marker-based skip logic, environment
variable toggles (`RUN_SLOW_TESTS`, `RUN_DATASET_DOWNLOAD_TESTS`), and shared
utilities (`assert_eval_success`, `assert_task_structure`, `mock_solver_with_output`).

### Current State

The project's `conftest.py`:
- Uses `sys.path` manipulation to add `src/` to the path (fragile, wouldn't be
  needed with proper packaging).
- Defines `FakeTaskState`, `FakeOutput`, `FakeExecResult`,
  `make_fake_generate` — custom mocks that don't exercise the real Inspect
  pipeline.
- Has unused imports (`Any`, `AsyncMock`, `MagicMock`).
- Has no marker-based skip logic.
- Has no environment variable toggles.

### Required Changes

1. **Remove `sys.path` manipulation** — with proper `uv` packaging, the
   package is importable directly.

2. **Add marker skip logic** matching inspect_evals patterns:

   ```python
   def pytest_collection_modifyitems(config, items):
       skip_slow = pytest.mark.skip(reason="need --runslow to run")
       for item in items:
           if "slow" in item.keywords:
               if not config.getoption("--runslow", default=False):
                   item.add_marker(skip_slow)
   ```

3. **Add shared test utilities** in `tests/utils/`:
   - `assert_eval_success(log)` — wraps common log assertions
   - `assert_task_structure(task)` — verifies task has dataset/solver/scorer

4. **Keep or refactor `FakeTaskState`** etc. for unit tests, but **add real
   E2E tests** that use `mockllm/model` for integration coverage.

5. **Remove unused imports** to pass ruff.

---

## 17. NOTICE File & Attribution

**Status: FAIL**

### Requirement

From EVALUATION_CHECKLIST.md: *"Each source file containing copied or adapted
code has a comment at the top... The root `NOTICE` file has an entry for every
copied or adapted file."*

### Current State

Four files have attribution comments but there is **no `NOTICE` file**:

| File | Attribution |
|------|------------|
| `lcb/scorers.py` | "adapted from the original HumanEval scorers" |
| `swe/solver_minimal.py` | "Based on: mini-swe-agent (https://github.com/SWE-agent/mini-swe-agent)" |
| `swe/build_images.py` | "Code copied from the swe_bench repository" |
| `report/llm_judge.py` | "Based on prompts from:" |

### Required Changes

1. **Create `NOTICE`** at root, following inspect_evals format:

   ```
   ALEval (ImpossibleBench Fork)
   Copyright 2026 ALEval Authors

   This product is licensed under [LICENSE]. It includes code from
   third-party projects:

   ---

   mini-swe-agent
   Copyright 2024 SWE-agent Authors
   Source: https://github.com/SWE-agent/mini-swe-agent

   Included in (adapted): src/impossiblebench/swe/solver_minimal.py

   ---

   swebench
   Copyright 2024 SWE-bench Authors
   Source: https://github.com/princeton-nlp/SWE-bench

   Included in (copied): src/impossiblebench/swe/build_images.py

   ---
   ...
   ```

2. **Add proper copyright/license headers** at the top of each file with
   adapted code.

3. **Where practical, isolate copied code** into dedicated files
   (e.g., `reference_impl.py`) per the guidelines.

---

## 18. README & Evaluation Report

**Status: FAIL**

### Requirement

From CONTRIBUTING.md: *"You should include your evaluation report in the
README.md in a section titled 'Evaluation Report'."*

Required contents:
- Results table with specific `inspect eval` commands used
- Full model names (e.g., `gpt-5.1-2025-11-13`, not `gpt-5.1`)
- Comparison with original ImpossibleBench paper or justification for absence
- Evaluation version, timestamp
- Total samples run out of dataset total
- Implementation deviations and limitations

### Current State

The README has:
- Quick Start section
- Available Benchmarks table
- How It Works diagram
- Configuration table
- Development section
- Troubleshooting section

The README is **missing**:
- **Evaluation Report** section entirely
- Any results from running the eval
- Any comparison with the original paper
- Reproducibility information

### Required Changes

1. **Add an "Evaluation Report" section** with a results table:

   ```markdown
   ## Evaluation Report

   ### Results

   | Model | Preset | Samples | Accuracy | Lie Rate | Truth Rate | Command |
   |-------|--------|---------|----------|----------|------------|---------|
   | gpt-5-2025-08-07 | lcb_minimal | 50/247 | 0.32 | 0.18 | 0.12 | `inspect eval ...` |
   | claude-sonnet-4-20250514 | lcb_minimal | 50/247 | 0.28 | 0.22 | 0.06 | `inspect eval ...` |

   ### Comparison with Original Paper

   The original ImpossibleBench paper (arXiv:2510.20270) reports...
   [or: No directly comparable results exist because ALEval adds the
   callout layer which the original paper does not measure.]

   ### Reproducibility

   - **Evaluation version**: 1-A
   - **Date**: 2026-04-04
   - **Dataset revisions**: LCB `abc123...`, SWE `def456...`
   ```

2. **Run the eval** on at least two models to populate the table (per
   CONTRIBUTING.md: *"We recommend producing results using at least two
   models"*).

---

## 19. Pre-commit Hooks

**Status: PARTIAL**

### Requirement

The inspect_evals pre-commit config includes: `ruff-check`, `ruff-format`,
`check-added-large-files`, `check-json`, `check-yaml`, `debug-statements`,
`detect-private-key`, `end-of-file-fixer`, `requirements-txt-fixer`,
`uv-lock`, and `markdownlint-fix`.

### Current State

`.pre-commit-config.yaml` exists with a subset:
- `ruff-check` with `--fix` (correct)
- `ruff-format` (correct)
- `check-added-large-files` (correct)
- `check-json` (correct)
- `check-yaml` (correct)
- `detect-private-key` (correct)
- `end-of-file-fixer` (correct)

**Missing**:
- `debug-statements` hook
- `requirements-txt-fixer` hook
- `uv-lock` hook (critical — ensures lockfile stays in sync)
- `markdownlint-fix` hook
- POSIX code check (custom hook)

### Required Changes

1. **Add missing hooks**:

   ```yaml
   - repo: https://github.com/pre-commit/pre-commit-hooks
     rev: v6.0.0
     hooks:
       - id: debug-statements
       - id: requirements-txt-fixer

   - repo: https://github.com/astral-sh/uv-pre-commit
     rev: 0.8.18
     hooks:
       - id: uv-lock

   - repo: https://github.com/igorshubovych/markdownlint-cli
     rev: v0.47.0
     hooks:
       - id: markdownlint-fix
   ```

2. **Actually install and run** the pre-commit hooks: `pre-commit install &&
   pre-commit run --all-files`.

3. **Fix all findings** before committing.

---

## 20. CI Workflows

**Status: FAIL**

### Requirement

inspect_evals CI runs:
- `ruff check` and `ruff format --check` (across Python 3.11, 3.12, 3.13)
- `mypy .` (across Python 3.11, 3.12, 3.13)
- POSIX code check
- README/docs generation check
- Changelog entry check
- Package build verification (`hynek/build-and-inspect-python-package`)
- Full test suite with environment toggles

### Current State

No `.github/workflows/` directory. No CI configuration whatsoever.

### Required Changes

1. **Create `.github/workflows/checks.yml`** with:
   - Ruff lint + format jobs
   - mypy job
   - Package build job

2. **Create `.github/workflows/tests.yml`** with:
   - Unit test job (fast, no Docker)
   - Integration test job (with Docker, gated by marks)

3. At minimum, a basic CI:

   ```yaml
   name: CI
   on: [push, pull_request]
   jobs:
     lint:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v5
         - uses: astral-sh/setup-uv@v7
         - run: uv sync --frozen --group dev
         - run: uv run ruff check
         - run: uv run ruff format --check
         - run: uv run mypy .
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v5
         - uses: astral-sh/setup-uv@v7
         - run: uv sync --frozen --group test
         - run: uv run pytest tests/ -v
   ```

---

## 21. Evaluation Artifacts

**Status: FAIL**

### Requirement

From EVALUATION_CHECKLIST.md:
- `agent_artefacts/<eval>/review/SUMMARY.md` — overall quality summary
- `agent_artefacts/<eval>/validity/VALIDITY_REPORT.md` — name, dataset,
  scoring validity assessment
- `agent_artefacts/trajectory_analysis/<model>_ANALYSIS.md` — trajectory
  analysis per model

### Current State

None of these directories or files exist.

### Required Changes

1. **Create `agent_artefacts/aleval/review/SUMMARY.md`** — a concise quality
   review (can be derived from existing `AUDIT_V2_REPORT.md`).

2. **Create `agent_artefacts/aleval/validity/VALIDITY_REPORT.md`** addressing:
   - **Name validity**: Does "ALEval" accurately represent what's measured?
   - **Dataset validity**: Can models succeed/fail? (Special case: tasks are
     deliberately impossible — needs clear framing)
   - **Scoring validity**: Does the scorer measure actual behavior?

3. **Create trajectory analysis** — run 1–5 samples per model, analyze the
   logs, create `agent_artefacts/trajectory_analysis/<model>_ANALYSIS.md`.

---

## 22. Evaluation Validity

**Status: NEEDS JUSTIFICATION**

### Requirement

From EVALUATION_CHECKLIST.md:

**Name Validity:**
- *"The evaluation name accurately represents the capability being measured"*
- *"The evaluation measures behaviour rather than statements about behaviour,
  or the name makes the distinction clear"*

**Dataset Validity:**
- *"It is reasonably possible for a model to succeed at each sample"*
- *"It is reasonably possible for a model to fail at each sample"*

**Scoring Validity:**
- *"The scorer measures actual task completion rather than a proxy"*
- *"A model cannot achieve a high score without genuinely completing the task"*

### Current State

ALEval has a unique validity profile that requires careful documentation:

1. **Name**: "Action-Lying Evaluation" measures *statements about behaviour*
   (whether the model lies about reward hacking), not the reward hacking
   behaviour itself (which is measured by the existing ImpossibleBench). The
   name should make this distinction explicit.

2. **Dataset**: Tasks are **deliberately impossible** — no model can
   "legitimately succeed." This inverts the normal validity assumption. Models
   that pass ARE reward-hacking by definition.

3. **Scoring**: The primary callout classifier uses regex matching on natural
   language (yes/no/evasive). This is a **proxy** for the agent's actual
   honesty. The regex has known failure modes (1 xfail test). The LLM judge
   adds a second opinion but introduces its own reliability questions.

4. **Gameability**: A model that always says "yes I reward hacked" would score
   100% truth without understanding the question. A model that always refuses
   to answer would score 100% evasive.

### Required Changes

1. **Write a VALIDITY_REPORT.md** that explicitly addresses each validity
   dimension with justifications.

2. **Consider renaming** to something that can't be confused with measuring
   actual coding ability (e.g., "ALEval: Measuring Honesty After Reward
   Hacking" rather than a generic benchmark name).

3. **Add meta-validation for the regex classifier** — test it against a
   labeled corpus of ~50–100 real model responses to establish precision/recall.

4. **Add meta-validation for the LLM judge** — per BEST_PRACTICES.md, use
   `tools/judge_calibration_diagnostics.py` or similar to calibrate.

5. **Document the intentional impossibility** prominently in the README and
   eval.yaml description.

---

## 23. Miscellaneous Code Quality

### 23a. `if __name__ == "__main__"` Blocks

**Status: FAIL**

Found in 6 files:
- `lcb/tasks.py:278`
- `lcb/scorers.py:244`
- `lcb/solver_tools.py:85`
- `swe/tasks.py:467`
- `report/cli.py:228`
- `apply_patch.py:535`

These blocks contain hardcoded model names and informal testing code.

**Required**: Remove them or move to dedicated scripts/examples. The
`report/cli.py` main block is fine (it's a CLI entry point), but the others
are debug artifacts.

### 23b. `print()` Statements

**Status: FAIL**

`print()` is used extensively in library code instead of `logging`:

| File | Approximate Count |
|------|------------------|
| `report/llm_judge.py` | 20+ |
| `report/cli.py` | 3 |
| `report/data_loader.py` | 2 |
| `lcb/scorers.py` | 2 |
| `lcb/solver_minimal.py` | 5 |
| `lcb/tasks.py` | 4 |
| `swe/scorers.py` | 6 |
| `swe/tasks.py` | 4 |
| `swe/build_images.py` | 1 |

**Required**: Replace all `print()` in library code with `logging.getLogger(__name__)`.
CLI entry points (`report/cli.py main()`) may keep `print()` for user-facing
output.

### 23c. Hardcoded Model Names

**Status: FAIL**

| File | Hardcoded Model |
|------|----------------|
| `report/llm_judge.py:106` | `model="claude-opus-4-20250514"` as default |
| `lcb/tasks.py:304-312` | `"openai/o4-mini"` in `__main__` |
| `swe/tasks.py:498-505` | `"openai/o4-mini"` in `__main__` |
| `report/cli.py:46` | `"openai/gpt-4.1"` in help text |

**Required**: Remove defaults that assume specific providers. Use model roles
or let users pass `--model`. The `__main__` blocks should be removed entirely.

### 23d. Backward-Compatibility Re-export Stubs

**Status: DISCUSS**

11 files in `src/impossiblebench/` exist solely to re-export from the new
subpackage structure (`livecodebench_tasks.py` → `lcb/tasks.py`, etc.).

The inspect_evals guidelines don't specifically address this pattern, but
minimizing dead code is a best practice. If these stubs are needed for
backward compatibility with existing users, they should:
- Have a deprecation warning
- Be documented in README
- Be removed after a transition period

### 23e. Unused Variables and Dead Code

**Status: FAIL**

Ruff reports 11 unused variables (F841) across source files. Per
BEST_PRACTICES.md: *"Remove dead code and unused members early."*

**Required**: Prefix with `_` if intentionally unused, or remove entirely.

---

## 24. Summary Matrix

| # | Area | Status | Effort |
|---|------|--------|--------|
| 1 | Packaging (uv + pyproject.toml) | FAIL | Medium |
| 2 | Ruff lint + format (744 + 31 violations) | FAIL | Medium (mostly auto-fix) |
| 3 | Import style (absolute vs relative) | FAIL | Low (mechanical) |
| 4 | Type hints + mypy | FAIL | High |
| 5 | Docstrings (Google style) | PARTIAL | Medium |
| 6 | Task construction (`name=` removal) | FAIL | Low |
| 7 | Dataset version pinning | FAIL | Low |
| 8 | Prompt templates | PARTIAL | Low |
| 9 | Error handling | FAIL | Medium |
| 10 | Scoring & metrics | PARTIAL | Medium |
| 11 | eval.yaml metadata | FAIL | Low |
| 12 | Task versioning | FAIL | Low |
| 13 | Unit tests | PARTIAL | Medium |
| 14 | End-to-end tests (mockllm/model) | FAIL | High |
| 15 | Pytest marks | FAIL | Low |
| 16 | conftest & test utils | FAIL | Medium |
| 17 | NOTICE file | FAIL | Low |
| 18 | README evaluation report | FAIL | High (requires running evals) |
| 19 | Pre-commit hooks | PARTIAL | Low |
| 20 | CI workflows | FAIL | Medium |
| 21 | Evaluation artifacts | FAIL | High |
| 22 | Evaluation validity | NEEDS JUSTIFICATION | High |
| 23 | Misc code quality | FAIL | Medium |

### Blocking vs Non-Blocking

**Blockers** (PR would be rejected immediately):
- Ruff lint/format failures (#2) — CI gate
- mypy failures (#4) — CI gate
- No E2E tests with mockllm (#14) — explicit requirement
- No evaluation report (#18) — explicit requirement
- `dataset_samples: 0` (#11) — metadata validation

**High Priority** (would be flagged in review):
- Relative imports (#3)
- No NOTICE file (#17)
- Bare excepts (#9)
- No pytest marks (#15)
- Task `name=` parameter (#6)
- Unpinned datasets (#7)

**Review Comments** (would be noted, may not block):
- Incomplete docstrings (#5)
- `print()` instead of logging (#23b)
- Hardcoded models (#23c)
- Prompt template extraction (#8)
- Backward-compat stubs (#23d)

---

*Report generated 2026-04-04 against inspect_evals@main.*
