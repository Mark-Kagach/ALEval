"""Shared test assertions following inspect_evals conventions."""

from __future__ import annotations


def assert_eval_success(log) -> None:
    """Assert that an eval log completed successfully with results."""
    assert log.status == "success", f"Eval failed with status: {log.status}"
    assert log.results is not None, "Eval produced no results"
    assert len(log.results.scores) > 0, "Eval produced no scores"


def assert_task_structure(task) -> None:
    """Assert that a task has the required components."""
    assert task.dataset is not None, "Task has no dataset"
    assert task.solver is not None, "Task has no solver"
    assert task.scorer is not None, "Task has no scorer"
