"""ImpossibleBench: Testing AI systems on impossible and edge-case scenarios.

This module contains solvers and datasets for testing AI systems on:
- SWE-bench impossible patches (conflicting, inverted, one-off)
- HumanEval/LiveCodeBench with impossible test cases
"""

# SWE-bench imports are optional for minimal LiveCodeBench usage.
try:
    from .swebench_tasks import (
        impossible_swebench,
        aleval_swebench_minimal,
        aleval_swebench_tools,
    )
    from .swebench_scorers import swe_bench_scorer
    from .swebench_agent_mini import mini_agent_solver
    from .swebench_agent_full import multi_submission_solver
except ImportError:
    impossible_swebench = None
    aleval_swebench_minimal = None
    aleval_swebench_tools = None
    swe_bench_scorer = None
    mini_agent_solver = None
    multi_submission_solver = None

# LiveCodeBench/HumanEval task imports
from .livecodebench_tasks import (
    impossible_livecodebench,
    aleval_livecodebench_minimal,
    aleval_livecodebench_tools,
)

# LiveCodeBench/HumanEval solver imports
from .livecodebench_agent_full import (
    swe_bench_style_humaneval_solver,
)
from .livecodebench_agent_mini import (
    agentic_humaneval_solver,
    minimal_humaneval_solver,
)

# LiveCodeBench/HumanEval scorer imports
from .livecodebench_scorers import (
    humaneval_scorer,
    agentic_humaneval_scorer,
    swe_style_humaneval_scorer,
)

__all__ = [
    # SWE-bench tasks
    "impossible_swebench",
    "aleval_swebench_minimal",
    "aleval_swebench_tools",
    "swe_bench_scorer",
    # SWE-bench agents
    "mini_agent_solver",
    "multi_submission_solver",
    # LiveCodeBench/HumanEval tasks
    "impossible_livecodebench",
    "aleval_livecodebench_minimal",
    "aleval_livecodebench_tools",
    # LiveCodeBench/HumanEval solvers
    "agentic_humaneval_solver",
    "swe_bench_style_humaneval_solver",
    "minimal_humaneval_solver",
    # LiveCodeBench/HumanEval scorers
    "humaneval_scorer",
    "agentic_humaneval_scorer",
    "swe_style_humaneval_scorer",
]