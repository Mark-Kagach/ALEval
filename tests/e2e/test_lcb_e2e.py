"""End-to-end tests for LiveCodeBench ALEval presets using mockllm/model.

These tests exercise the full Inspect AI pipeline: task creation, solver
execution, scoring, and metric computation. They download the HuggingFace
dataset and run in a local sandbox.
"""

from __future__ import annotations

import pytest
from inspect_ai import eval
from inspect_ai.model import ModelOutput

from impossiblebench.lcb.tasks import (
    aleval_livecodebench_minimal,
    aleval_livecodebench_tools,
)


@pytest.mark.dataset_download
@pytest.mark.huggingface
@pytest.mark.slow(60)
def test_aleval_lcb_minimal_e2e_default() -> None:
    """LCB minimal preset runs to completion with default (empty) mock output."""
    [log] = eval(
        tasks=aleval_livecodebench_minimal(limit=1, sandbox="local"),
        model="mockllm/model",
    )
    assert log.status == "success"
    assert log.results is not None
    assert log.samples is not None
    assert len(log.samples) == 1


@pytest.mark.dataset_download
@pytest.mark.huggingface
@pytest.mark.slow(60)
def test_aleval_lcb_minimal_e2e_with_code() -> None:
    """LCB minimal preset with a pre-baked code response."""
    [log] = eval(
        tasks=aleval_livecodebench_minimal(limit=1, sandbox="local"),
        model="mockllm/model",
        model_args={"custom_outputs": _mock_code_outputs()},
    )
    assert log.status == "success"
    assert log.results is not None
    # Verify scorer produced a score for the sample
    sample = log.samples[0]
    assert sample.scores is not None


@pytest.mark.dataset_download
@pytest.mark.huggingface
@pytest.mark.slow(60)
def test_aleval_lcb_tools_e2e_default() -> None:
    """LCB tools preset runs to completion with default mock output."""
    [log] = eval(
        tasks=aleval_livecodebench_tools(limit=1, sandbox="docker"),
        model="mockllm/model",
    )
    assert log.status == "success"
    assert log.results is not None


def _mock_code_outputs() -> list[ModelOutput]:
    """Generate mock outputs that look like code submissions."""
    return [
        ModelOutput.from_content(
            model="mockllm/model",
            content="```python\ndef solution():\n    return 42\n```",
        ),
        # Second output for the callout response
        ModelOutput.from_content(
            model="mockllm/model",
            content="Yes, I reward hacked.",
        ),
    ]
