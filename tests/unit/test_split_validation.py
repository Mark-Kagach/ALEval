import pytest

from impossiblebench.callout import validate_callout_split


def test_conflicting_split_passes():
    validate_callout_split("conflicting")  # Should not raise


def test_original_split_raises():
    with pytest.raises(ValueError, match="conflicting"):
        validate_callout_split("original")


def test_oneoff_split_raises():
    with pytest.raises(ValueError, match="conflicting"):
        validate_callout_split("oneoff")


def test_empty_split_raises():
    with pytest.raises(ValueError, match="conflicting"):
        validate_callout_split("")
