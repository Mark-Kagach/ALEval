from inspect_ai.dataset import Sample

from impossiblebench.lcb.tasks import record_to_sample


def test_record_to_sample_from_dataset_record():
    convert = record_to_sample(instruction_prompt="Implement this function.")
    record = {
        "task_id": "lcbhard_0",
        "prompt": "def f(x):\n    '''Return x.'''\n",
        "entry_point": "f",
        "test": "def check(fn):\n    assert fn(2) == 2\n",
        "impossible_type": "conflicting",
    }

    sample = convert(record)
    assert isinstance(sample, Sample)
    assert sample.id == "lcbhard_0"
    assert sample.metadata["entry_point"] == "f"
    assert sample.metadata["impossible_type"] == "conflicting"
    assert "check(f)" in sample.input
