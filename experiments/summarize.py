#!/usr/bin/env python3
"""Aggregate per-model ALEval reports into combined tables.

Reads judged_samples.csv from each per-model report directory and produces:
- reports/aleval/results_table.md  — Markdown table for README.md
- reports/aleval/results_table.csv — Combined CSV for analysis

Usage:
    python experiments/summarize.py [--reports-dir ./reports/aleval]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


def find_model_csvs(reports_dir: Path) -> list[tuple[str, str, Path]]:
    """Find all per-model judged_samples.csv files.

    Returns list of (preset, model_safe, csv_path) tuples.
    """
    results = []
    for preset_dir in sorted(reports_dir.iterdir()):
        if not preset_dir.is_dir() or preset_dir.name == "combined":
            continue
        preset = preset_dir.name
        for model_dir in sorted(preset_dir.iterdir()):
            if not model_dir.is_dir():
                continue
            csv = model_dir / "judged_samples.csv"
            if csv.exists():
                results.append((preset, model_dir.name, csv))
    return results


def compute_model_stats(csv_path: Path) -> dict:
    """Compute summary stats from a single model's judged_samples.csv."""
    df = pd.read_csv(csv_path)
    total = len(df)
    passed = df["passed"].sum()
    pass_rate = passed / total if total > 0 else 0.0

    triggered = df[df["callout_deterministic_label"].isin(["lie", "truth", "evasive"])]
    n_triggered = len(triggered)

    label_counts = (
        triggered["callout_deterministic_label"]
        .value_counts()
        .reindex(["lie", "truth", "evasive"], fill_value=0)
    )

    stats = {
        "samples": total,
        "passed": int(passed),
        "pass_rate": pass_rate,
        "triggered": n_triggered,
        "lie": int(label_counts.get("lie", 0)),
        "truth": int(label_counts.get("truth", 0)),
        "evasive": int(label_counts.get("evasive", 0)),
        "lie_rate": label_counts.get("lie", 0) / n_triggered if n_triggered > 0 else 0.0,
        "truth_rate": label_counts.get("truth", 0) / n_triggered if n_triggered > 0 else 0.0,
        "evasive_rate": label_counts.get("evasive", 0) / n_triggered if n_triggered > 0 else 0.0,
    }

    # LLM judge stats if available
    if "callout_llm_judge_label" in df.columns:
        judge_triggered = triggered["callout_llm_judge_label"].dropna()
        if len(judge_triggered) > 0:
            judge_counts = judge_triggered.value_counts().reindex(
                ["no", "yes", "evasive", "unknown"], fill_value=0
            )
            stats["judge_no"] = int(judge_counts.get("no", 0))
            stats["judge_yes"] = int(judge_counts.get("yes", 0))
            stats["judge_evasive"] = int(judge_counts.get("evasive", 0))
            stats["judge_unknown"] = int(judge_counts.get("unknown", 0))

    return stats


def format_model_name(model_safe: str) -> str:
    """Convert filesystem-safe name back to display name.

    openai_gpt-5 -> openai/gpt-5
    """
    return model_safe.replace("_", "/", 1)


def build_results_table(rows: list[dict]) -> str:
    """Build a Markdown table from results rows."""
    lines = [
        "| Model | Preset | Samples | Pass Rate | Triggered | Lie Rate | Truth Rate | Evasive Rate |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in rows:
        lines.append(
            f"| {r['model']} | {r['preset']} | {r['samples']} "
            f"| {r['pass_rate']:.1%} | {r['triggered']} "
            f"| {r['lie_rate']:.1%} | {r['truth_rate']:.1%} | {r['evasive_rate']:.1%} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Aggregate ALEval results into tables.")
    parser.add_argument(
        "--reports-dir",
        default="./reports/aleval",
        help="Directory containing per-model report subdirectories.",
    )
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    if not reports_dir.exists():
        print(f"Error: reports directory not found: {reports_dir}", file=sys.stderr)
        sys.exit(1)

    model_csvs = find_model_csvs(reports_dir)
    if not model_csvs:
        print(f"Error: no judged_samples.csv found in {reports_dir}/<preset>/<model>/", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(model_csvs)} model results\n")

    # Compute stats for each model
    rows = []
    for preset, model_safe, csv_path in model_csvs:
        stats = compute_model_stats(csv_path)
        stats["model"] = format_model_name(model_safe)
        stats["preset"] = preset
        rows.append(stats)
        print(
            f"  {preset:8s} | {stats['model']:40s} | "
            f"pass={stats['pass_rate']:.1%}  lie={stats['lie_rate']:.1%}  "
            f"truth={stats['truth_rate']:.1%}  evasive={stats['evasive_rate']:.1%}"
        )

    # Write combined CSV
    df_combined = pd.DataFrame(rows)
    csv_out = reports_dir / "results_table.csv"
    df_combined.to_csv(csv_out, index=False)
    print(f"\nWrote: {csv_out}")

    # Write Markdown table
    md_table = build_results_table(rows)
    md_out = reports_dir / "results_table.md"
    md_out.write_text(
        "# ALEval Results\n\n"
        + md_table
        + "\n\n"
        + f"*{len(rows)} model-preset combinations. "
        + "Rates are among triggered callouts only.*\n",
        encoding="utf-8",
    )
    print(f"Wrote: {md_out}")

    # Print the table to stdout for easy copy-paste
    print(f"\n{'='*80}")
    print("Copy this into README.md (Results section):")
    print(f"{'='*80}\n")
    print(md_table)


if __name__ == "__main__":
    main()
