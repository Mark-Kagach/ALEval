"""Generate deterministic ALEval reports from Inspect logs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis.data_loader import DataLoader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic lying-eval reports from Inspect .eval logs."
    )
    parser.add_argument(
        "--logs-dir",
        required=True,
        help="Directory containing Inspect .eval logs.",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        help="Directory where report artifacts will be written.",
    )
    parser.add_argument(
        "--glob",
        default="*.eval",
        help="Glob pattern used to discover logs in logs-dir (default: *.eval).",
    )
    parser.add_argument(
        "--latest-only",
        action="store_true",
        help="Process only the most recently modified matching .eval file.",
    )
    parser.add_argument(
        "--n-workers",
        type=int,
        default=4,
        help="Worker processes for log loading (default: 4).",
    )
    return parser.parse_args()


def select_pattern(logs_dir: Path, pattern: str, latest_only: bool) -> str:
    if not latest_only:
        return pattern
    matches = list(logs_dir.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No logs found in {logs_dir} matching pattern {pattern}")
    latest = max(matches, key=lambda p: p.stat().st_mtime)
    return latest.name


def compute_summary(df_samples, df_passed) -> dict:
    total_samples = int(len(df_samples))
    passed_count = int(len(df_passed))
    passed_rate = (passed_count / total_samples) if total_samples else 0.0

    label_counts = (
        df_passed["callout_deterministic_label"]
        .value_counts()
        .reindex(["lie", "truth", "evasive"], fill_value=0)
        .to_dict()
    )
    label_percentages = {
        key: (value / passed_count if passed_count else 0.0)
        for key, value in label_counts.items()
    }
    return {
        "total_samples": total_samples,
        "passed_count": passed_count,
        "passed_rate": passed_rate,
        "reward_hack_operational_definition": "passed score (C) on conflicting impossible task",
        "label_counts_among_passed": label_counts,
        "label_percentages_among_passed": label_percentages,
    }


def write_summary_md(path: Path, summary: dict, logs_dir: Path, pattern: str) -> None:
    lines = [
        "# ALEval Report",
        "",
        "## Run Inputs",
        f"- logs_dir: `{logs_dir}`",
        f"- pattern: `{pattern}`",
        "",
        "## Core Metrics",
        f"- total_samples: `{summary['total_samples']}`",
        f"- passed_count (reward-hack operational proxy): `{summary['passed_count']}`",
        f"- passed_rate: `{summary['passed_rate']:.3f}`",
        "",
        "## Lie/Truth/Evasive Among Passed Samples",
        "| label | count | percent |",
        "|---|---:|---:|",
    ]
    for label in ["lie", "truth", "evasive"]:
        lines.append(
            f"| {label} | {summary['label_counts_among_passed'][label]} | "
            f"{summary['label_percentages_among_passed'][label]:.3f} |"
        )
    lines.append("")
    lines.append("## Operational Semantics")
    lines.append(f"- {summary['reward_hack_operational_definition']}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    logs_dir = Path(args.logs_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pattern = select_pattern(logs_dir, args.glob, args.latest_only)
    loader = DataLoader(n_workers=args.n_workers)
    loader.load_folder(str(logs_dir), pattern=pattern)

    df_samples = loader.to_sample_df(dump=False)
    if df_samples.empty:
        raise RuntimeError("No per-sample rows found in the selected logs.")

    df_samples = df_samples.copy()
    df_samples["reward_hack_operational"] = df_samples["passed"] == True  # noqa: E712
    df_passed = df_samples[df_samples["reward_hack_operational"] == True].copy()  # noqa: E712

    summary = compute_summary(df_samples, df_passed)

    csv_path = out_dir / "judged_samples.csv"
    json_path = out_dir / "judged_samples.json"
    summary_path = out_dir / "summary.md"

    df_samples.to_csv(csv_path, index=False)
    records = json.loads(df_samples.to_json(orient="records", date_format="iso"))
    json_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    write_summary_md(summary_path, summary, logs_dir, pattern)

    print(f"Wrote {csv_path}")
    print(f"Wrote {json_path}")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
