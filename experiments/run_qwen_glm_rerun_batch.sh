#!/usr/bin/env bash
# ============================================================================
# Run a focused 8-job ALEval rerun batch for Qwen/GLM across LCB and SWE.
#
# LCB:
#   - qwen3.6-plus on lcb-min
#   - qwen3.6-plus on lcb-tools
#   - glm-5.1 on lcb-min
#   - glm-5.1 on lcb-tools
#   - max_attempts=5, message_limit=60
#
# SWE:
#   - qwen3.6-plus on swe-min
#   - qwen3.6-plus on swe-tools
#   - glm-5.1 on swe-min
#   - glm-5.1 on swe-tools
#   - max_attempts=3, message_limit=100
#
# Default sample limit is 5 so this stays in "smoke / validation" territory.
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export LOG_BASE="${LOG_BASE:-./logs/aleval_qwen_glm_rerun}"
export REPORT_BASE="${REPORT_BASE:-./reports/aleval_qwen_glm_rerun}"
source "$SCRIPT_DIR/config.sh"

LIMIT="${1:-5}"
RUNNER_DIR="${LOG_BASE}/_runner_qwen_glm_rerun"

mkdir -p "$RUNNER_DIR"

RUNS=(
    "openrouter/qwen/qwen3.6-plus|lcb-min|5|60"
    "openrouter/qwen/qwen3.6-plus|lcb-tools|5|60"
    "openrouter/z-ai/glm-5.1|lcb-min|5|60"
    "openrouter/z-ai/glm-5.1|lcb-tools|5|60"
    "openrouter/qwen/qwen3.6-plus|swe-min|3|100"
    "openrouter/qwen/qwen3.6-plus|swe-tools|3|100"
    "openrouter/z-ai/glm-5.1|swe-min|3|100"
    "openrouter/z-ai/glm-5.1|swe-tools|3|100"
)

echo "=== Qwen/GLM ALEval rerun batch ==="
echo "Limit per run: $LIMIT"
echo "Logs: $LOG_BASE"
echo "Reports: $REPORT_BASE"
echo "Runner logs: $RUNNER_DIR"
echo ""

launch_job() {
    local model="$1"
    local preset="$2"
    local max_attempts="$3"
    local message_limit="$4"
    local model_safe
    model_safe=$(sanitize_model "$model")

    local runner_log="${RUNNER_DIR}/${preset}__${model_safe}.log"
    local status_file="${RUNNER_DIR}/${preset}__${model_safe}.status"

    rm -f "$status_file"

    (
        echo "[$(date -Is)] START $preset $model limit=$LIMIT attempts=$max_attempts message_limit=$message_limit"

        if [[ "$preset" == swe-* ]]; then
            env \
                LOG_BASE="$LOG_BASE" \
                MAX_ATTEMPTS="$max_attempts" \
                MESSAGE_LIMIT_SWE_MIN="$message_limit" \
                MESSAGE_LIMIT_SWE_TOOLS="$message_limit" \
                "$SCRIPT_DIR/run_model.sh" "$model" "$preset" "$LIMIT"
        else
            env \
                LOG_BASE="$LOG_BASE" \
                MAX_ATTEMPTS="$max_attempts" \
                MESSAGE_LIMIT_MIN="$message_limit" \
                MESSAGE_LIMIT_TOOLS="$message_limit" \
                "$SCRIPT_DIR/run_model.sh" "$model" "$preset" "$LIMIT"
        fi

        echo "success" >"$status_file"
        echo "[$(date -Is)] SUCCESS $preset $model"
    ) >"$runner_log" 2>&1 || {
        echo "failed" >"$status_file"
        echo "[$(date -Is)] FAILED $preset $model" >>"$runner_log"
    } &
}

for spec in "${RUNS[@]}"; do
    IFS="|" read -r model preset max_attempts message_limit <<<"$spec"
    launch_job "$model" "$preset" "$max_attempts" "$message_limit"
done

wait || true

echo ""
echo "=== Qwen/GLM rerun summary ==="
SUCCESS_COUNT=0
FAILED_COUNT=0

for spec in "${RUNS[@]}"; do
    IFS="|" read -r model preset _ _ <<<"$spec"
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
echo "  LOG_BASE=$LOG_BASE REPORT_BASE=$REPORT_BASE ./experiments/collect_results.sh --judge"

if (( FAILED_COUNT > 0 )); then
    exit 1
fi
