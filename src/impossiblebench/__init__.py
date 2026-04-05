"""ImpossibleBench: Testing AI systems on impossible and edge-case scenarios.

This module contains solvers and datasets for testing AI systems on:
- SWE-bench impossible patches (conflicting, inverted, one-off)
- HumanEval/LiveCodeBench with impossible test cases

Canonical subpackage layout:
- impossiblebench.lcb     — LiveCodeBench solvers, scorers, tasks
- impossiblebench.swe     — SWE-bench solvers, scorers, tasks
- impossiblebench.report  — CLI reporting, data loading, LLM judge
"""

# SWE-bench imports are optional for minimal LiveCodeBench usage.
try:
    from impossiblebench.swe.scorers import swe_bench_scorer
    from impossiblebench.swe.solver_minimal import mini_agent_solver
    from impossiblebench.swe.solver_tools import multi_submission_solver
    from impossiblebench.swe.tasks import (
        aleval_swebench_minimal,
        aleval_swebench_tools,
        impossible_swebench,
    )
except ImportError:
    impossible_swebench = None
    aleval_swebench_minimal = None
    aleval_swebench_tools = None
    swe_bench_scorer = None
    mini_agent_solver = None
    multi_submission_solver = None

# LiveCodeBench/HumanEval task imports
# LiveCodeBench/HumanEval scorer imports
from impossiblebench.lcb.scorers import (
    agentic_humaneval_scorer,
    humaneval_scorer,
    swe_style_humaneval_scorer,
)
from impossiblebench.lcb.solver_minimal import (
    agentic_humaneval_solver,
    minimal_humaneval_solver,
)

# LiveCodeBench/HumanEval solver imports
from impossiblebench.lcb.solver_tools import (
    swe_bench_style_humaneval_solver,
)
from impossiblebench.lcb.tasks import (
    aleval_livecodebench_minimal,
    aleval_livecodebench_tools,
    impossible_livecodebench,
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
