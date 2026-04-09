"""End-to-end tests for SWE-bench ALEval presets using mockllm/model.

These tests require Docker and the SWE-bench optional dependency.
They exercise the full pipeline: task creation, Docker sandbox setup,
solver execution, scoring, and metric computation.
"""

from __future__ import annotations

import pytest
from inspect_ai import eval

from impossiblebench.swe.tasks import (
    aleval_swebench_minimal,
    aleval_swebench_tools,
)


@pytest.mark.dataset_download
@pytest.mark.huggingface
@pytest.mark.docker
@pytest.mark.slow(180)
def test_aleval_swe_minimal_e2e_default() -> None:
    """SWE-bench minimal preset runs to completion with default mock output."""
    [log] = eval(
        tasks=aleval_swebench_minimal(limit=1),
        model="mockllm/model",
    )
    assert log.status == "success"
    assert log.results is not None
    assert log.samples is not None
    assert len(log.samples) == 1


@pytest.mark.dataset_download
@pytest.mark.huggingface
@pytest.mark.docker
@pytest.mark.slow(180)
def test_aleval_swe_tools_e2e_default() -> None:
    """SWE-bench tools preset runs to completion with default mock output."""
    [log] = eval(
        tasks=aleval_swebench_tools(limit=1),
        model="mockllm/model",
    )
    assert log.status == "success"
    assert log.results is not None
    assert log.samples is not None
    assert len(log.samples) == 1
