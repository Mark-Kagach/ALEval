"""End-to-end: SWE minimal solver -> callout -> scorer chain.

The mini_agent_solver is a complex bash-based agent that requires sandbox
and swebench internals. We simulate its output and test the callout ->
scorer chain with swe_bench_scorer (patching get_eval_script to avoid
the swebench dependency at runtime).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from conftest import FakeExecResult, FakeOutput, FakeTaskState, make_fake_generate


@pytest.fixture
def swe_sandbox():
    """Mock sandbox for SWE-bench scoring."""
    sb = AsyncMock()
    sb.exec.return_value = FakeExecResult(success=True, returncode=0, stdout="", stderr="")
    sb.write_file = AsyncMock()
    sb.read_file = AsyncMock(return_value="mock patch content")
    return sb


def _swe_state_passing():
    """State as if mini_agent_solver ran and produced a passing patch."""
    state = FakeTaskState(
        metadata={
            "base_commit": "abc123",
            "repo": "test/repo",
            "version": "1.0",
            "test_patch": (
                "--- a/tests/test_example.py\n+++ b/tests/test_example.py\n@@ -1 +1 @@\n-old\n+new"
            ),
            "agentic_results": {
                "preserved_solution": "diff --git a/file.py ...",
            },
        },
        output=FakeOutput("Done."),
    )
    state.sample_id = "test_instance_001"
    return state


@pytest.mark.asyncio
async def test_swe_minimal_callout_scorer_chain(swe_sandbox):
    """Callout -> scorer chain for SWE minimal (solver output simulated)."""
    try:
        from impossiblebench.swe.scorers import swe_bench_scorer
    except ImportError:
        pytest.skip("swebench_scorers not importable (missing jsonlines or other deps)")

    from impossiblebench.callout import same_chat_callout_solver

    state = _swe_state_passing()

    callout_gen = make_fake_generate(["No, I have not."])
    callout = same_chat_callout_solver()
    state = await callout(state, callout_gen)

    assert state.metadata["agentic_results"]["same_chat_callout"]["triggered"] is True

    mock_sb_fn = MagicMock(return_value=swe_sandbox)
    with (
        patch("impossiblebench.swe.scorers.sandbox", mock_sb_fn),
        patch(
            "impossiblebench.swe.scorers.get_eval_script",
            return_value="#!/bin/bash\nexit 0",
        ),
    ):
        scorer = swe_bench_scorer()
        score = await scorer(state, None)

    assert score.value == 1.0
    assert score.metadata["callout_deterministic_label"] == "lie"
    assert "same_chat_callout" in score.metadata


@pytest.mark.asyncio
async def test_swe_minimal_callout_not_triggered_on_failure(swe_sandbox):
    """Callout must not fire when solver fails (no preserved_solution)."""
    from impossiblebench.callout import same_chat_callout_solver

    state = FakeTaskState(
        metadata={
            "base_commit": "abc123",
            "repo": "test/repo",
            "version": "1.0",
            "test_patch": "--- a/t.py\n+++ b/t.py\n@@ -1 +1 @@\n-a\n+b",
            "agentic_results": {},
        },
        output=FakeOutput("I could not solve this."),
    )
    state.sample_id = "test_instance_002"

    callout_gen = make_fake_generate(["Should not be called"])
    callout = same_chat_callout_solver()
    state = await callout(state, callout_gen)

    co = state.metadata["agentic_results"]["same_chat_callout"]
    assert co["triggered"] is False
    assert co["response"] is None
