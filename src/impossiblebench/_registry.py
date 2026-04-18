"""Inspect task registry for package-qualified task loading.

Importing these task factories is enough for Inspect to discover them through
the ``inspect_ai`` setuptools entry point declared in ``pyproject.toml``.
"""

from impossiblebench.lcb.tasks import (
    aleval_livecodebench_minimal,
    aleval_livecodebench_tools,
    impossible_livecodebench,
)
from impossiblebench.swe.tasks import (
    aleval_swebench_minimal,
    aleval_swebench_tools,
    impossible_swebench,
)

__all__ = [
    "aleval_livecodebench_minimal",
    "aleval_livecodebench_tools",
    "impossible_livecodebench",
    "aleval_swebench_minimal",
    "aleval_swebench_tools",
    "impossible_swebench",
]
