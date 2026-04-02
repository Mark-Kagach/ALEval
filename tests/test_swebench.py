from types import SimpleNamespace

import pytest
from inspect_ai.dataset import Sample

from impossiblebench import swebench_tasks


class FakeDataset(list):
    def filter(self, predicate):
        return FakeDataset([s for s in self if predicate(s)])

    def shuffle(self, seed=42):
        return None

    def __getitem__(self, item):
        value = super().__getitem__(item)
        if isinstance(item, slice):
            return FakeDataset(value)
        return value


def _fake_hf_dataset(**kwargs):
    return FakeDataset(
        [
            Sample(
                id="inst_1",
                input="Fix bug.",
                target="",
                metadata={
                    "base_commit": "abc123",
                    "patch": "",
                    "PASS_TO_PASS": "[]",
                    "FAIL_TO_PASS": "[]",
                    "test_patch": "",
                    "original_test_patch": "",
                    "version": "v1",
                    "repo": "owner/repo",
                    "environment_setup_commit": "",
                    "hints_text": "",
                    "created_at": "",
                    "impossible_type": "original",
                    "first_fail_to_pass_test": "",
                    "difficulty": "easy",
                },
            )
        ]
    )


def test_impossible_swebench_invalid_split_raises():
    with pytest.raises(ValueError):
        swebench_tasks.impossible_swebench(split="bad", agent_type="minimal", build_docker_images=False)


def test_impossible_swebench_task_construction(monkeypatch):
    monkeypatch.setattr(swebench_tasks, "hf_dataset", _fake_hf_dataset)
    monkeypatch.setattr(swebench_tasks, "find_spec", lambda _: object())

    task = swebench_tasks.impossible_swebench(
        split="original",
        agent_type="minimal",
        build_docker_images=False,
        docker_image_from_id=lambda _: "dummy:latest",
        limit=1,
        sandbox_type="docker",
    )
    assert task.name.startswith("swebench_original")
    assert len(task.dataset) == 1
