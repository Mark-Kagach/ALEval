"""Build and optionally execute balanced ALEval experiment commands."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run or print ALEval campaign commands.")
    parser.add_argument("--manifest", required=True, help="Path to campaign manifest YAML.")
    parser.add_argument("--logs-root", default="./logs/campaigns", help="Root log output directory.")
    parser.add_argument("--dry-run", action="store_true", help="Only print commands.")
    parser.add_argument("--max-attempts", type=int, default=3, help="max_attempts task parameter.")
    parser.add_argument("--message-limit", type=int, default=60, help="message_limit task parameter.")
    return parser.parse_args()


def build_command(task: str, model: str, log_dir: str, max_attempts: int, message_limit: int) -> list[str]:
    return [
        "inspect",
        "eval",
        task,
        "--model",
        model,
        "--log-dir",
        log_dir,
        "-T",
        f"max_attempts={max_attempts}",
        "-T",
        f"message_limit={message_limit}",
    ]


def main() -> None:
    args = parse_args()
    manifest = yaml.safe_load(Path(args.manifest).read_text(encoding="utf-8"))

    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    campaign_name = manifest["campaign_name"]
    campaign_dir = Path(args.logs_root) / f"{campaign_name}_{timestamp}"
    campaign_dir.mkdir(parents=True, exist_ok=True)

    commands = []
    for model in manifest["models"]:
        model_id = model["id"]
        for task in manifest["tasks"]:
            model_slug = model_id.replace("/", "__")
            task_slug = task.split("@")[-1]
            task_log_dir = campaign_dir / model_slug / task_slug
            task_log_dir.mkdir(parents=True, exist_ok=True)
            commands.append(
                build_command(
                    task=task,
                    model=model_id,
                    log_dir=str(task_log_dir),
                    max_attempts=args.max_attempts,
                    message_limit=args.message_limit,
                )
            )

    (campaign_dir / "commands.json").write_text(
        json.dumps(commands, indent=2),
        encoding="utf-8",
    )

    for cmd in commands:
        print(" ".join(cmd))
        if not args.dry_run:
            subprocess.run(cmd, check=True)

    print(f"Wrote campaign commands to {campaign_dir / 'commands.json'}")


if __name__ == "__main__":
    main()
