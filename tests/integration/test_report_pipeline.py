"""End-to-end tests for the aleval-report pipeline functions."""

from pathlib import Path

import pandas as pd

from impossiblebench.report.cli import compute_summary, write_summary_md


def test_compute_summary_counts_labels():
    """Summary must count lie/truth/evasive among triggered callouts."""
    df_samples = pd.DataFrame(
        [
            {"passed": True, "callout_deterministic_label": "lie"},
            {"passed": True, "callout_deterministic_label": "truth"},
            {"passed": True, "callout_deterministic_label": "lie"},
            {"passed": False, "callout_deterministic_label": "lie"},
            {"passed": False, "callout_deterministic_label": "not_applicable"},
        ]
    )
    df_passed = df_samples[df_samples["passed"]].copy()
    df_triggered = df_samples[
        df_samples["callout_deterministic_label"].isin(["lie", "truth", "evasive"])
    ].copy()

    summary = compute_summary(df_samples, df_passed, df_triggered)

    assert summary["total_samples"] == 5
    assert summary["passed_count"] == 3
    assert summary["triggered_count"] == 4
    assert summary["label_counts_among_triggered"]["lie"] == 3
    assert summary["label_counts_among_triggered"]["truth"] == 1
    assert summary["label_counts_among_triggered"]["evasive"] == 0


def test_compute_summary_handles_zero_passed():
    """Summary must not crash when no samples passed or triggered."""
    df_samples = pd.DataFrame(
        [
            {"passed": False, "callout_deterministic_label": "not_applicable"},
        ]
    )
    df_passed = df_samples[df_samples["passed"]].copy()
    df_triggered = df_samples[
        df_samples["callout_deterministic_label"].isin(["lie", "truth", "evasive"])
    ].copy()

    summary = compute_summary(df_samples, df_passed, df_triggered)
    assert summary["passed_count"] == 0
    assert summary["triggered_count"] == 0
    assert summary["label_percentages_among_triggered"]["lie"] == 0.0


def test_write_summary_md_creates_valid_markdown(tmp_path):
    """Written summary.md must contain expected headers and table."""
    summary = {
        "total_samples": 10,
        "passed_count": 3,
        "passed_rate": 0.3,
        "triggered_count": 5,
        "reward_hack_operational_definition": "...",
        "label_counts_among_triggered": {"lie": 2, "truth": 1, "evasive": 0},
        "label_percentages_among_triggered": {"lie": 0.667, "truth": 0.333, "evasive": 0.0},
    }
    path = tmp_path / "summary.md"
    write_summary_md(path, summary, Path("./logs"), "*.eval")

    content = path.read_text()
    assert "# ALEval Report" in content
    assert "| lie | 2 |" in content
    assert "| truth | 1 |" in content
    assert "callout_triggered_count" in content
