#!/usr/bin/env bash
# ============================================================================
# Run ALEval experiment phases defined in config.sh
# Usage: ./experiments/run_all.sh [phase]
#
# Phases:
#   smoke         - 3 samples on first LCB minimal model only
#   smoke-matrix  - 5 samples on every model across lcb/swe min/tools
#   minimal       - Full LCB minimal on all MODELS_MINIMAL
#   tools         - Full LCB tools on MODELS_TOOLS
#   swe-min       - Full SWE minimal on all MODELS_MINIMAL
#   swe-tools     - Full SWE tools on all MODELS_MINIMAL
#   all           - lcb minimal + lcb tools (default)
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

PHASE="${1:-all}"
FAILED=()
COMPLETED=()

run_model() {
    local model="$1" preset="$2" limit="${3:-}"
    local model_safe
    model_safe=$(sanitize_model "$model")

    echo ""
    echo "================================================================"
    echo "  Starting: $preset | $model"
    echo "================================================================"

    if "$SCRIPT_DIR/run_model.sh" "$model" "$preset" "$limit"; then
        COMPLETED+=("${preset}:${model_safe}")
    else
        echo "WARNING: Failed: $preset | $model (continuing...)"
        FAILED+=("${preset}:${model_safe}")
    fi
}

case "$PHASE" in
    smoke)
        echo "=== Phase: Smoke Test (${SMOKE_LIMIT} samples) ==="
        run_model "${MODELS_MINIMAL[0]}" "lcb-min" "$SMOKE_LIMIT"
        ;;
    smoke-matrix)
        "$SCRIPT_DIR/run_parallel_smoke_matrix.sh"
        ;;
    minimal)
        echo "=== Phase: Full LCB Minimal (${#MODELS_MINIMAL[@]} models x $LCB_CONFLICTING_COUNT tasks) ==="
        for model in "${MODELS_MINIMAL[@]}"; do
            run_model "$model" "lcb-min"
        done
        ;;
    tools)
        echo "=== Phase: Full LCB Tools (${#MODELS_TOOLS[@]} models x $LCB_CONFLICTING_COUNT tasks) ==="
        for model in "${MODELS_TOOLS[@]}"; do
            run_model "$model" "lcb-tools"
        done
        ;;
    swe-min)
        echo "=== Phase: Full SWE Minimal (${#MODELS_MINIMAL[@]} models x requested task count) ==="
        for model in "${MODELS_MINIMAL[@]}"; do
            run_model "$model" "swe-min"
        done
        ;;
    swe-tools)
        echo "=== Phase: Full SWE Tools (${#MODELS_MINIMAL[@]} models x requested task count) ==="
        for model in "${MODELS_MINIMAL[@]}"; do
            run_model "$model" "swe-tools"
        done
        ;;
    all)
        echo "=== Phase: All (lcb minimal + lcb tools) ==="
        for model in "${MODELS_MINIMAL[@]}"; do
            run_model "$model" "lcb-min"
        done
        for model in "${MODELS_TOOLS[@]}"; do
            run_model "$model" "lcb-tools"
        done
        ;;
    *)
        echo "Usage: $0 [smoke|smoke-matrix|minimal|tools|swe-min|swe-tools|all]"
        exit 1
        ;;
esac

echo ""
echo "================================================================"
echo "  EXPERIMENT SUMMARY"
echo "================================================================"
echo "  Completed: ${#COMPLETED[@]}"
for c in "${COMPLETED[@]:-}"; do
    [[ -n "$c" ]] && echo "    + $c"
done
if [[ ${#FAILED[@]} -gt 0 ]]; then
    echo "  Failed: ${#FAILED[@]}"
    for f in "${FAILED[@]}"; do
        echo "    - $f"
    done
fi
echo "================================================================"
