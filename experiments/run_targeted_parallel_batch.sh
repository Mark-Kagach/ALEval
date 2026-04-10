#!/usr/bin/env bash
# ============================================================================
# Run a targeted 4-job parallel ALEval batch:
#   - glm-5.1 on lcb-min
#   - qwen3.6-plus on lcb-tools
#   - glm-5.1 on swe-min
#   - qwen3.6-plus on swe-tools
#
# Defaults:
#   - limit=5
#   - max_attempts=3
#   - message_limit=100 for all scaffolds
#
# This script is intended for a small, controlled cross-scaffold smoke run.
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export LOG_BASE="${LOG_BASE:-./logs/aleval_targeted_clean}"
export REPORT_BASE="${REPORT_BASE:-./reports/aleval_targeted_clean}"
export MAX_ATTEMPTS="${MAX_ATTEMPTS:-3}"
export MESSAGE_LIMIT_MIN="${MESSAGE_LIMIT_MIN:-100}"
export MESSAGE_LIMIT_TOOLS="${MESSAGE_LIMIT_TOOLS:-100}"
export MESSAGE_LIMIT_SWE_MIN="${MESSAGE_LIMIT_SWE_MIN:-100}"
export MESSAGE_LIMIT_SWE_TOOLS="${MESSAGE_LIMIT_SWE_TOOLS:-100}"
source "$SCRIPT_DIR/config.sh"

LIMIT="${1:-5}"
RUNNER_DIR="${LOG_BASE}/_runner_targeted_batch"

mkdir -p "$RUNNER_DIR"

RUNS=(
    "openrouter/z-ai/glm-5.1|lcb-min"
    "openrouter/qwen/qwen3.6-plus|lcb-tools"
    "openrouter/z-ai/glm-5.1|swe-min"
    "openrouter/qwen/qwen3.6-plus|swe-tools"
)

echo "=== Targeted parallel ALEval batch ==="
echo "Limit per run: $LIMIT"
echo "max_attempts: $MAX_ATTEMPTS"
echo "message limits: lcb-min=$MESSAGE_LIMIT_MIN lcb-tools=$MESSAGE_LIMIT_TOOLS swe-min=$MESSAGE_LIMIT_SWE_MIN swe-tools=$MESSAGE_LIMIT_SWE_TOOLS"
echo "Runner logs: $RUNNER_DIR"
echo ""

launch_job() {
    local model="$1"
    local preset="$2"
    local model_safe
    model_safe=$(sanitize_model "$model")

    local runner_log="${RUNNER_DIR}/${preset}__${model_safe}.log"
    local status_file="${RUNNER_DIR}/${preset}__${model_safe}.status"

    rm -f "$status_file"

    (
        echo "[$(date -Is)] START $preset $model limit=$LIMIT"
        if "$SCRIPT_DIR/run_model.sh" "$model" "$preset" "$LIMIT"; then
            echo "success" >"$status_file"
            echo "[$(date -Is)] SUCCESS $preset $model"
        else
            echo "failed" >"$status_file"
            echo "[$(date -Is)] FAILED $preset $model"
            exit 1
        fi
    ) >"$runner_log" 2>&1 &
}

for spec in "${RUNS[@]}"; do
    model="${spec%%|*}"
    preset="${spec##*|}"
    launch_job "$model" "$preset"
done

wait || true

echo ""
echo "=== Targeted batch summary ==="
SUCCESS_COUNT=0
FAILED_COUNT=0

for spec in "${RUNS[@]}"; do
    model="${spec%%|*}"
    preset="${spec##*|}"
    model_safe=$(sanitize_model "$model")
    status_file="${RUNNER_DIR}/${preset}__${model_safe}.status"
    runner_log="${RUNNER_DIR}/${preset}__${model_safe}.log"

    if [[ -f "$status_file" ]] && [[ "$(cat "$status_file")" == "success" ]]; then
        echo "  + ${preset}:${model_safe}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "  - ${preset}:${model_safe} (see $runner_log)"
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
done

echo ""
echo "Success: $SUCCESS_COUNT"
echo "Failed:  $FAILED_COUNT"
echo "Then run:"
echo "  ./experiments/collect_results.sh --judge"

if (( FAILED_COUNT > 0 )); then
    exit 1
fi
