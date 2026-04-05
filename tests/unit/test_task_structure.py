"""Verify ALEval task structure without running evals."""

from __future__ import annotations

import pytest


@pytest.mark.dataset_download
@pytest.mark.huggingface
def test_aleval_lcb_minimal_task_structure() -> None:
    """Verify LCB minimal task has dataset, solver, and scorer."""
    from impossiblebench.lcb.tasks import aleval_livecodebench_minimal

    task = aleval_livecodebench_minimal(limit=1)
    assert task.dataset is not None
    assert task.solver is not None
    assert task.scorer is not None
