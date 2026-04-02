"""Aggregate campaign logs into a single sample-level artifact table."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from impossiblebench.analysis.data_loader import DataLoader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export campaign-wide ALEval artifacts.")
    parser.add_argument("--logs-root", required=True, help="Campaign log root directory.")
    parser.add_argument("--out-dir", required=True, help="Output directory.")
    parser.add_argument("--pattern", default="*.eval", help="Eval log glob pattern.")
    parser.add_argument("--n-workers", type=int, default=4, help="Parallel workers.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logs_root = Path(args.logs_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    all_rows: list[pd.DataFrame] = []
    for candidate in logs_root.rglob("*"):
        if candidate.is_dir() and list(candidate.glob(args.pattern)):
            loader = DataLoader(n_workers=args.n_workers)
            loader.load_folder(str(candidate), pattern=args.pattern, show_progress=False)
            sample_df = loader.to_sample_df(dump=False)
            if sample_df.empty:
                continue
            sample_df["log_folder"] = str(candidate)
            all_rows.append(sample_df)

    if not all_rows:
        raise RuntimeError(f"No sample rows found under {logs_root}")

    merged = pd.concat(all_rows, ignore_index=True)
    merged.to_csv(out_dir / "campaign_samples.csv", index=False)
    merged.to_json(out_dir / "campaign_samples.json", orient="records", indent=2)

    summary = (
        merged.groupby(["model", "dataset", "variant", "agent_type"], dropna=False)["passed"]
        .mean()
        .reset_index(name="pass_rate")
    )
    summary.to_csv(out_dir / "campaign_summary.csv", index=False)
    print(f"Wrote artifacts to {out_dir}")


if __name__ == "__main__":
    main()
