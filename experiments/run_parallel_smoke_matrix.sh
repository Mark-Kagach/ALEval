#!/usr/bin/env bash
# ============================================================================
# Run a parallel 5-sample smoke matrix across all models and presets.
#
# By default this runs every model in MODELS_MINIMAL across:
#   - lcb-min
#   - lcb-tools
#   - swe-min
#   - swe-tools
#
# Usage:
#   ./experiments/run_parallel_smoke_matrix.sh
#   ./experiments/run_parallel_smoke_matrix.sh [limit] [parallel_jobs]
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

LIMIT="${1:-$SMOKE_MATRIX_LIMIT}"
MAX_JOBS="${2:-$PARALLEL_JOBS}"
PRESETS=("lcb-min" "lcb-tools" "swe-min" "swe-tools")
RUNNER_DIR="${LOG_BASE}/_runner_smoke_matrix"

mkdir -p "$RUNNER_DIR"

echo "=== Parallel smoke matrix ==="
echo "Models: ${#MODELS_MINIMAL[@]}"
echo "Presets: ${PRESETS[*]}"
echo "Limit per run: $LIMIT"
echo "Max parallel jobs: $MAX_JOBS"
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

active_jobs() {
    jobs -pr | wc -l | tr -d ' '
}

for preset in "${PRESETS[@]}"; do
    for model in "${MODELS_MINIMAL[@]}"; do
        while (( $(active_jobs) >= MAX_JOBS )); do
            if ! wait -n; then
                :
            fi
        done
        launch_job "$model" "$preset"
    done
done

while (( $(active_jobs) > 0 )); do
    if ! wait -n; then
        :
    fi
done

echo ""
echo "=== Smoke matrix summary ==="
SUCCESS_COUNT=0
FAILED_COUNT=0

for preset in "${PRESETS[@]}"; do
    for model in "${MODELS_MINIMAL[@]}"; do
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
done

echo ""
echo "Success: $SUCCESS_COUNT"
echo "Failed:  $FAILED_COUNT"
echo "Reports can be generated with: ./experiments/collect_results.sh --judge"

if (( FAILED_COUNT > 0 )); then
    exit 1
fi
