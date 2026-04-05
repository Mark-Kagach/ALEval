"""Shared test fixtures and configuration for ALEval tests."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TESTS_DIR = Path(__file__).resolve().parent

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    run_slow = config.getoption("--runslow") or os.environ.get("RUN_SLOW_TESTS", "").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    run_dataset = os.environ.get("RUN_DATASET_DOWNLOAD_TESTS", "yes").lower() not in (
        "0",
        "false",
        "no",
        "off",
    )

    skip_slow = pytest.mark.skip(reason="need --runslow option or RUN_SLOW_TESTS=1")
    skip_dataset = pytest.mark.skip(reason="dataset download tests disabled")

    for item in items:
        if "slow" in item.keywords and not run_slow:
            item.add_marker(skip_slow)
        if "dataset_download" in item.keywords and not run_dataset:
            item.add_marker(skip_dataset)


@dataclass
class FakeOutput:
    """Mock for inspect_ai model output."""

    completion: str


@dataclass
class FakeExecResult:
    """Mock for sandbox exec result."""

    success: bool
    returncode: int
    stdout: str
    stderr: str


class FakeTaskState:
    """Minimal TaskState stand-in for unit tests."""

    def __init__(
        self,
        metadata: dict | None = None,
        messages: list | None = None,
        output: FakeOutput | None = None,
    ) -> None:
        self.metadata = metadata or {}
        self.messages = messages or []
        self.output = output or FakeOutput("")
        self.completed = False


def make_fake_generate(responses: list[str]):
    """Return an async callable that returns pre-scripted responses in order."""
    call_count = 0

    async def fake_generate(state):
        nonlocal call_count
        response = responses[call_count % len(responses)]
        call_count += 1
        state.output = FakeOutput(completion=response)
        return state

    return fake_generate


@pytest.fixture
def passing_state() -> FakeTaskState:
    """State where a solver has set preserved_solution (model passed)."""
    return FakeTaskState(
        metadata={
            "agentic_results": {
                "preserved_solution": "def f(x): return x + 1",
            }
        },
        messages=[],
    )


@pytest.fixture
def failing_state() -> FakeTaskState:
    """State where no preserved_solution is set (model failed)."""
    return FakeTaskState(
        metadata={"agentic_results": {}},
        messages=[],
    )
