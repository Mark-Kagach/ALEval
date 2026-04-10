#!/usr/bin/env bash
# ============================================================================
# Run full LCB-min in parallel for GPT-5.4 and Claude Opus 4.6.
#
# Defaults:
#   - full 103-task LCB conflicting split
#   - max_attempts=5
#   - message_limit=60
#   - same base settings as other LCB-min runs
#
# Optional env overrides:
#   - MAX_CONNECTIONS=<n>  # Inspect API concurrency
#   - MAX_SAMPLES=<n>      # Inspect sample concurrency
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export LOG_BASE="${LOG_BASE:-./logs/aleval_lcb_min_gpt_claude}"
export REPORT_BASE="${REPORT_BASE:-./reports/aleval_lcb_min_gpt_claude}"
export MAX_ATTEMPTS="${MAX_ATTEMPTS:-5}"
export MESSAGE_LIMIT_MIN="${MESSAGE_LIMIT_MIN:-60}"
source "$SCRIPT_DIR/config.sh"

LIMIT="${1:-}"
RUNNER_DIR="${LOG_BASE}/_runner_lcb_min_gpt_claude"

mkdir -p "$RUNNER_DIR"

RUNS=(
    "openrouter/openai/gpt-5.4"
    "openrouter/anthropic/claude-opus-4.6"
)

echo "=== Full LCB-min GPT/Claude subset ==="
if [[ -n "$LIMIT" ]]; then
    echo "Task limit: $LIMIT"
else
    echo "Task limit: full (${LCB_CONFLICTING_COUNT})"
fi
echo "max_attempts: $MAX_ATTEMPTS"
echo "message_limit: $MESSAGE_LIMIT_MIN"
if [[ -n "${MAX_CONNECTIONS:-}" ]]; then
    echo "max_connections: $MAX_CONNECTIONS"
fi
if [[ -n "${MAX_SAMPLES:-}" ]]; then
    echo "max_samples: $MAX_SAMPLES"
fi
echo "Logs: $LOG_BASE"
echo "Reports: $REPORT_BASE"
echo "Runner logs: $RUNNER_DIR"
echo ""

launch_job() {
    local model="$1"
    local model_safe
    model_safe=$(sanitize_model "$model")

    local runner_log="${RUNNER_DIR}/lcb-min__${model_safe}.log"
    local status_file="${RUNNER_DIR}/lcb-min__${model_safe}.status"

    rm -f "$status_file"

    (
        echo "[$(date -Is)] START lcb-min $model limit=${LIMIT:-full}"

        if [[ -n "$LIMIT" ]]; then
            "$SCRIPT_DIR/run_model.sh" "$model" "lcb-min" "$LIMIT"
        else
            "$SCRIPT_DIR/run_model.sh" "$model" "lcb-min"
        fi

        echo "success" >"$status_file"
        echo "[$(date -Is)] SUCCESS lcb-min $model"
    ) >"$runner_log" 2>&1 || {
        echo "failed" >"$status_file"
        echo "[$(date -Is)] FAILED lcb-min $model" >>"$runner_log"
    } &
}

for model in "${RUNS[@]}"; do
    launch_job "$model"
done

wait || true

echo ""
echo "=== LCB-min GPT/Claude summary ==="
SUCCESS_COUNT=0
FAILED_COUNT=0

for model in "${RUNS[@]}"; do
    model_safe=$(sanitize_model "$model")
    status_file="${RUNNER_DIR}/lcb-min__${model_safe}.status"
    runner_log="${RUNNER_DIR}/lcb-min__${model_safe}.log"

    if [[ -f "$status_file" ]] && [[ "$(cat "$status_file")" == "success" ]]; then
        echo "  + lcb-min:${model_safe}"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "  - lcb-min:${model_safe} (see $runner_log)"
        FAILED_COUNT=$((FAILED_COUNT + 1))
    fi
done

echo ""
echo "Success: $SUCCESS_COUNT"
echo "Failed:  $FAILED_COUNT"
echo "Then run:"
echo "  LOG_BASE=$LOG_BASE REPORT_BASE=$REPORT_BASE ./experiments/collect_results.sh --judge"

if (( FAILED_COUNT > 0 )); then
    exit 1
fi
