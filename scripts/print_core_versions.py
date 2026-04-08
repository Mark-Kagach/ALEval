"""Print versions of core ALEval dependencies (for env parity checks)."""
from __future__ import annotations

import importlib.metadata
import sys


def _ver(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


def main() -> None:
    pkgs = [
        "inspect_ai",
        "datasets",
        "pandas",
        "impossiblebench",
    ]
    print("executable:", sys.executable)
    print("python:", sys.version.split()[0])
    for p in pkgs:
        print(f"{p}: {_ver(p)}")


if __name__ == "__main__":
    main()
