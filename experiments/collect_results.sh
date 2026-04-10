#!/usr/bin/env bash
# ============================================================================
# Generate reports from experiment logs
# Usage: ./experiments/collect_results.sh [--judge]
#
# Generates per-model and combined reports. Pass --judge to add LLM judge.
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

USE_JUDGE=false
if [[ "${1:-}" == "--judge" ]]; then
    USE_JUDGE=true
fi

# ---------------------------------------------------------------------------
# Per-model reports
# ---------------------------------------------------------------------------
echo "=== Generating per-model reports ==="

for preset_dir in "$LOG_BASE"/*/; do
    [[ -d "$preset_dir" ]] || continue
    preset=$(basename "$preset_dir")

    for model_dir in "$preset_dir"*/; do
        [[ -d "$model_dir" ]] || continue
        model_safe=$(basename "$model_dir")

        # Check if there are .eval files
        if ! ls "$model_dir"*.eval &>/dev/null; then
            echo "  Skip: $preset/$model_safe (no .eval files)"
            continue
        fi

        out_dir="${REPORT_BASE}/${preset}/${model_safe}"
        mkdir -p "$out_dir"

        echo "  Reporting: $preset / $model_safe"

        CMD=(aleval-report --logs-dir "$model_dir" --out-dir "$out_dir")
        if $USE_JUDGE; then
            CMD+=(--llm-judge "$JUDGE_MODEL")
        fi

        "${CMD[@]}"
    done
done

# ---------------------------------------------------------------------------
# Combined report (all models, all presets)
# ---------------------------------------------------------------------------
echo ""
echo "=== Generating combined report ==="

# Collect all .eval files into a flat temp dir via symlinks
COMBINED_LOGS=$(mktemp -d)
trap "rm -rf $COMBINED_LOGS" EXIT

for eval_file in "$LOG_BASE"/*/*/*.eval; do
    [[ -f "$eval_file" ]] || continue
    ln -sf "$(realpath "$eval_file")" "$COMBINED_LOGS/$(basename "$eval_file")"
done

COMBINED_OUT="${REPORT_BASE}/combined"
mkdir -p "$COMBINED_OUT"

CMD=(aleval-report --logs-dir "$COMBINED_LOGS" --out-dir "$COMBINED_OUT")
if $USE_JUDGE; then
    CMD+=(--llm-judge "$JUDGE_MODEL")
fi

"${CMD[@]}"

echo ""
echo "=== Reports complete ==="
echo "Per-model: $REPORT_BASE/<preset>/<model>/"
echo "Combined:  $COMBINED_OUT/"
echo ""
echo "Next: python experiments/summarize.py"
