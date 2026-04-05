"""Unit tests for record_to_sample conversion functions."""

from __future__ import annotations

from impossiblebench.lcb.tasks import record_to_sample


def test_lcb_record_to_sample_basic() -> None:
    """Verify record_to_sample produces a Sample with correct fields."""
    converter = record_to_sample()
    record = {
        "task_id": "lcbhard_42",
        "prompt": "def two_sum(nums, target):\n    '''Find two numbers that add to target.'''\n",
        "entry_point": "two_sum",
        "test": "def check(candidate):\n    assert candidate([2,7], 9) == [0,1]\n",
        "impossible_type": "conflicting",
    }
    sample = converter(record)
    assert sample.id == "lcbhard_42"
    assert "two_sum" in sample.input
    assert sample.metadata["entry_point"] == "two_sum"
    assert sample.metadata["impossible_type"] == "conflicting"
    assert sample.metadata["task_id"] == "lcbhard_42"


def test_lcb_record_to_sample_preserves_test_patch() -> None:
    """Verify test_patch is stored when allow_test_modifications=False."""
    converter = record_to_sample(allow_test_modifications=False)
    record = {
        "task_id": "lcbhard_1",
        "prompt": "def f(x):\n    pass\n",
        "entry_point": "f",
        "test": "def check(c):\n    assert c(1) == 2\n",
        "impossible_type": "original",
    }
    sample = converter(record)
    assert "test_patch" in sample.metadata
    assert sample.metadata["test_patch"] == record["test"]
