#!/bin/bash
# NGAFID ML Pipeline Master Script
# Usage: ./scripts/run_all.sh --model cnn --size_ratio 0.1 --debug true

# Default parameters
DATASET="ngafid"
SIZE_RATIO="0.1"
MODEL="cnn"
DEBUG="true"
TASK="all"

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --dataset) DATASET="$2"; shift ;;
        --size_ratio) SIZE_RATIO="$2"; shift ;;
        --model) MODEL="$2"; shift ;;
        --debug) DEBUG="$2"; shift ;;
        --task) TASK="$2"; shift ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo "Starting NGAFID Production Pipeline..."
echo "Model: $MODEL | Size Ratio: $SIZE_RATIO | Debug: $DEBUG"

python main.py --dataset "$DATASET" --size_ratio "$SIZE_RATIO" --model "$MODEL" --debug "$DEBUG" --task "$TASK"
