#!/usr/bin/env bash
# ============================================================================
# Run a single model evaluation
# Usage: ./experiments/run_model.sh <model> <preset> [limit]
#
# Examples:
#   ./experiments/run_model.sh openrouter/openai/gpt-5.4 lcb-min        # Full 103 tasks
#   ./experiments/run_model.sh openrouter/openai/gpt-5.4 lcb-tools      # Full 103 tasks
#   ./experiments/run_model.sh openrouter/openai/gpt-5.4 swe-min 5      # 5-sample SWE smoke
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

MODEL="${1:?Usage: $0 <model> <preset> [limit]}"
PRESET="${2:?Usage: $0 <model> <preset> [limit]}"
LIMIT="${3:-}"  # Empty = all 103 tasks

# Resolve task and params
PRESET_SAFE="$PRESET"
USE_SANDBOX_FLAG=true
SANDBOX="local"
MSG_LIMIT="$MESSAGE_LIMIT_MIN"
TASK_ARGS=()

case "$PRESET" in
    minimal | lcb-min)
        TASK="$TASK_LCB_MIN"
        SANDBOX="local"
        MSG_LIMIT="$MESSAGE_LIMIT_MIN"
        PRESET_SAFE="lcb-min"
        ;;
    tools | lcb-tools)
        TASK="$TASK_LCB_TOOLS"
        SANDBOX="docker"
        MSG_LIMIT="$MESSAGE_LIMIT_TOOLS"
        PRESET_SAFE="lcb-tools"
        ;;
    swe-min)
        TASK="$TASK_SWE_MIN"
        USE_SANDBOX_FLAG=false
        MSG_LIMIT="$MESSAGE_LIMIT_SWE_MIN"
        PRESET_SAFE="swe-min"
        TASK_ARGS+=(-T "sandbox_type=docker")
        ;;
    swe-tools)
        TASK="$TASK_SWE_TOOLS"
        USE_SANDBOX_FLAG=false
        MSG_LIMIT="$MESSAGE_LIMIT_SWE_TOOLS"
        PRESET_SAFE="swe-tools"
        TASK_ARGS+=(-T "sandbox_type=docker")
        ;;
    *)
        echo "Error: preset must be one of 'lcb-min', 'lcb-tools', 'swe-min', 'swe-tools' (aliases: minimal, tools), got '$PRESET'"
        exit 1
        ;;
esac

# Build log directory: logs/aleval/<preset>/<model_safe>/
MODEL_SAFE=$(sanitize_model "$MODEL")
LOG_DIR="${LOG_BASE}/${PRESET_SAFE}/${MODEL_SAFE}"
mkdir -p "$LOG_DIR"

# Build inspect eval command
CMD=(
    inspect eval "$TASK"
    --model "$MODEL"
    -T "max_attempts=${MAX_ATTEMPTS}"
    -T "message_limit=${MSG_LIMIT}"
    --log-dir "$LOG_DIR"
)

if [[ -n "${MAX_CONNECTIONS:-}" ]]; then
    CMD+=(--max-connections "$MAX_CONNECTIONS")
fi

if [[ -n "${MAX_SAMPLES:-}" ]]; then
    CMD+=(--max-samples "$MAX_SAMPLES")
fi

if $USE_SANDBOX_FLAG; then
    CMD+=(--sandbox "$SANDBOX")
fi

if [[ ${#TASK_ARGS[@]} -gt 0 ]]; then
    CMD+=("${TASK_ARGS[@]}")
fi

if [[ -n "$LIMIT" ]]; then
    CMD+=(-T "limit=${LIMIT}")
fi

# Print and execute
echo "============================================"
echo "  ALEval: $PRESET_SAFE | $MODEL"
if $USE_SANDBOX_FLAG; then
    echo "  Tasks: ${LIMIT:-$LCB_CONFLICTING_COUNT} | Sandbox: $SANDBOX"
else
    echo "  Tasks: ${LIMIT:-$LCB_CONFLICTING_COUNT} | Sandbox: task-defined docker"
fi
echo "  Logs: $LOG_DIR"
echo "============================================"
echo ""
echo "Running: ${CMD[*]}"
echo ""

"${CMD[@]}"

echo ""
echo "Done. Logs written to: $LOG_DIR"
