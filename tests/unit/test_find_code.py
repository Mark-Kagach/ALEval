import pytest

from impossiblebench.lcb.scorers import find_code


def test_extracts_python_block():
    text = "Here's my solution:\n```python\ndef f(x): return x\n```"
    assert find_code(text) == "def f(x): return x\n"


@pytest.mark.xfail(
    reason="Generic ``` pattern captures inter-block text as last match, overshadowing python blocks"
)
def test_extracts_last_python_block_when_multiple():
    """Ideally the last ```python block should be returned, but the generic
    pattern's inter-block capture ends up last in the concatenated match list."""
    text = "```python\nfirst\n```\nActually:\n```python\nsecond\n```"
    assert find_code(text) == "second\n"


def test_extracts_generic_code_block():
    text = "```\ndef f(x): return x\n```"
    assert find_code(text) == "def f(x): return x\n"


def test_returns_raw_when_no_blocks():
    text = "def f(x): return x"
    assert find_code(text) == "def f(x): return x"


def test_empty_completion():
    assert find_code("") == ""


def test_block_with_language_tag_variation():
    text = "```Python\ndef f(): pass\n```"
    result = find_code(text)
    assert "def f(): pass" in result
