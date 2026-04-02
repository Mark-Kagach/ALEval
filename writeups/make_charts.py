"""Generate basic chart assets from campaign summary tables."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create chart PNGs for writeups.")
    parser.add_argument("--samples-csv", required=True, help="Path to campaign_samples.csv.")
    parser.add_argument("--out-dir", required=True, help="Directory for generated plots.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.samples_csv)
    grouped = (
        df.groupby(["model", "dataset", "variant", "agent_type"], dropna=False)["passed"]
        .mean()
        .reset_index(name="pass_rate")
    )

    for dataset in grouped["dataset"].dropna().unique():
        subset = grouped[grouped["dataset"] == dataset]
        pivot = subset.pivot_table(
            index="model",
            columns=["variant", "agent_type"],
            values="pass_rate",
            fill_value=0.0,
        )
        ax = pivot.plot(kind="bar", figsize=(12, 6))
        ax.set_title(f"{dataset}: pass rate by split and scaffold")
        ax.set_ylabel("pass_rate")
        ax.set_xlabel("model")
        plt.tight_layout()
        plt.savefig(out_dir / f"{dataset}_pass_rate.png", dpi=200)
        plt.close()

    print(f"Wrote charts to {out_dir}")


if __name__ == "__main__":
    main()
