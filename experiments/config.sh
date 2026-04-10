#!/usr/bin/env bash
# ============================================================================
# ALEval Experiment Configuration
# ============================================================================
# Edit this file to configure your experiment. All other scripts source this.
# ============================================================================

# ---------------------------------------------------------------------------
# Models — EDIT THESE
# ---------------------------------------------------------------------------
# Full minimal experiment (103 tasks each). Add/remove as needed.
# Format: openrouter/<provider>/<model>
MODELS_MINIMAL=(
    "openrouter/qwen/qwen3.6-plus"
    "openrouter/z-ai/glm-5.1"
    "openrouter/x-ai/grok-4.20"
    "openrouter/google/gemini-3.1-pro-preview"
    "openrouter/openai/gpt-5.4"
    "openrouter/anthropic/claude-opus-4.6"
)

# Tools experiment (103 tasks each). Pick 2-3 best performers after minimal.
MODELS_TOOLS=(
    "openrouter/z-ai/glm-5.1"
    "openrouter/qwen/qwen3.6-plus"
)

# ---------------------------------------------------------------------------
# Task parameters
# ---------------------------------------------------------------------------
MAX_ATTEMPTS="${MAX_ATTEMPTS:-5}"                # Max solver submission attempts per sample
MESSAGE_LIMIT_MIN="${MESSAGE_LIMIT_MIN:-60}"     # Max conversation turns (LCB minimal scaffold)
MESSAGE_LIMIT_TOOLS="${MESSAGE_LIMIT_TOOLS:-60}" # Max conversation turns (LCB tools scaffold)
SMOKE_LIMIT="${SMOKE_LIMIT:-3}"                  # Samples for smoke test
MESSAGE_LIMIT_SWE_MIN="${MESSAGE_LIMIT_SWE_MIN:-60}"     # Max conversation turns (SWE minimal scaffold)
MESSAGE_LIMIT_SWE_TOOLS="${MESSAGE_LIMIT_SWE_TOOLS:-60}" # Max conversation turns (SWE tools scaffold)
SMOKE_MATRIX_LIMIT="${SMOKE_MATRIX_LIMIT:-5}"            # Samples per model/preset for matrix runs
PARALLEL_JOBS="${PARALLEL_JOBS:-4}"                      # Max concurrent jobs for matrix runs

# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------
LOG_BASE="${LOG_BASE:-./logs/aleval}"
REPORT_BASE="${REPORT_BASE:-./reports/aleval}"

# ---------------------------------------------------------------------------
# LLM Judge
# ---------------------------------------------------------------------------
JUDGE_MODEL="${JUDGE_MODEL:-openrouter/z-ai/glm-5.1}"

# ---------------------------------------------------------------------------
# Derived (do not edit below)
# ---------------------------------------------------------------------------
TASK_LCB_MIN="src/impossiblebench/lcb/tasks.py@aleval_livecodebench_minimal"
TASK_LCB_TOOLS="src/impossiblebench/lcb/tasks.py@aleval_livecodebench_tools"
TASK_SWE_MIN="src/impossiblebench/swe/tasks.py@aleval_swebench_minimal"
TASK_SWE_TOOLS="src/impossiblebench/swe/tasks.py@aleval_swebench_tools"
LCB_CONFLICTING_COUNT=103  # Verified from HuggingFace

# Create a filesystem-safe name from a model ID
# openrouter/openai/gpt-5 -> openai_gpt-5
sanitize_model() {
    echo "$1" | sed 's|^openrouter/||' | tr '/' '_'
}
