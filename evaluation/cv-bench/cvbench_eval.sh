#!/bin/bash

set -e

SRC_DIR="/path/to/data/cv-bench"
BASE_DIR="./"
DATA_DIR="$BASE_DIR/generated_imgs"

ADE_EVAL_SCRIPT="/path/to/evaluation/cv-bench/eval/ade/api_eval_new.py"
COCO_EVAL_SCRIPT="/path/to/evaluation/cv-bench/eval/coco/api_eval_new.py"
OMNI_EVAL_SCRIPT="/path/to/evaluation/cv-bench/eval/omni/api_eval_new.py"
MERGE_SCRIPT="/path/to/evaluation/cv-bench/merge_results_final.py"
CALCULATE_SCRIPT="/path/to/evaluation/cv-bench/calculate_score.py"

# API Key
API_KEY="YOUR_API_KEY_HERE"
MODEL_NAME="gpt-4o-mini-2024-07-18"
BASE_URL="YOUR_BASE_URL_HERE"

echo "================================================="
echo "Model name: $MODEL_NAME"
echo "Data dir: $DATA_DIR"
echo ""


if [ ! -d "$DATA_DIR" ]; then
    echo "Error: '$DATA_DIR' does not exist. Please ensure the data directory is correct."
    exit 1
fi

MODEL_PREFIX=$(echo "$MODEL_NAME" | tr '/' '_')
ANSWERS_ADE_FILE="$DATA_DIR/${MODEL_PREFIX}_answers_ade.jsonl"
ANSWERS_COCO_FILE="$DATA_DIR/${MODEL_PREFIX}_answers_coco.jsonl"
ANSWERS_OMNI_FILE="$DATA_DIR/${MODEL_PREFIX}_answers_omni.jsonl"
MERGED_CSV_FILE="$DATA_DIR/${MODEL_PREFIX}_merged_results.csv"
FINAL_SCORE_FILE="$DATA_DIR/${MODEL_PREFIX}_final_scores.csv"



echo "--- [step 0] Copy annotations.jsonl ---"
python /path/to/evaluation/cv-bench/copy_annotations.py \
    --src_root "$SRC_DIR" \
    --base_dir "$BASE_DIR"
echo "--- annotations.jsonl Copy done ---"




echo "--- [Step 1/3] Run Inference ---"
echo "  -> Eval ADE20K..."
python "$ADE_EVAL_SCRIPT" \
    --data_root "$DATA_DIR" \
    --api_key "$API_KEY" \
    --model_name "$MODEL_NAME" \
    --base_url "$BASE_URL" \
    --answers_file "$ANSWERS_ADE_FILE"
echo "  -> ADE20K Eval done."

echo "  -> Eval COCO..."
python "$COCO_EVAL_SCRIPT" \
    --data_root "$DATA_DIR" \
    --api_key "$API_KEY" \
    --model_name "$MODEL_NAME" \
    --base_url "$BASE_URL" \
    --answers_file "$ANSWERS_COCO_FILE"
echo "  -> COCO Eval done."

echo "  -> Eval Omni3D..."
python "$OMNI_EVAL_SCRIPT" \
    --data_root "$DATA_DIR" \
    --api_key "$API_KEY" \
    --model_name "$MODEL_NAME" \
    --base_url "$BASE_URL" \
    --answers_file "$ANSWERS_OMNI_FILE"
echo "  -> Omni3D Eval done."
echo "--- All Inference done. ---"
echo ""


echo "--- [Step 2/3] Merge Results ---"
python "$MERGE_SCRIPT" \
    --base_dir "$DATA_DIR" \
    --input_files "$(basename "$ANSWERS_ADE_FILE")" "$(basename "$ANSWERS_COCO_FILE")" "$(basename "$ANSWERS_OMNI_FILE")" \
    --output_csv_file "$MERGED_CSV_FILE"
echo "--- Merge Results done. ---"
echo ""


echo "--- [Step 3/3] Calculate Score ---"
python "$CALCULATE_SCRIPT" \
    --input_csv "$MERGED_CSV_FILE" \
    --output_csv "$FINAL_SCORE_FILE"
echo "--- Calculate Score done. ---"
echo ""


echo "================================================="
echo "=== All process done! ==="
echo "================================================="
echo "All result files are saved: $DATA_DIR"
echo "Final score file: $FINAL_SCORE_FILE"
echo "================================================="
