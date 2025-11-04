#!/bin/bash
set -euo pipefail

# ================= Config =================
src_json_root="/path/to/data/mmmu/mmmu_dev_processed_single_img_subset"
cache_dir="/path/to/MMMU"

data_dir="./generated_imgs"
output_path="./predictions"

base_url="YUOR_BASE_URL_HERE"
api_key="YOUR_API_KEY_HERE"
model="gpt-4o-mini-2024-07-18"

echo "================= Step 1 ================="
python /path/to/evaluation/mmmu/prepare_output_jsons.py \
  --src_json_root "$src_json_root" \
  --dst_root "$data_dir" \
  --overwrite

echo "================= Step 2 ================="
python /path/to/evaluation/mmmu/run_api_local_images.py \
  --data_path "$data_dir" \
  --output_path "$output_path" \
  --base_url "$base_url" \
  --api_key "$api_key" \
  --model "$model" \
  --cache_dir "$cache_dir"

echo "================= Step 3 ================="
python /path/to/evaluation/mmmu/split_outputs_by_subject.py \
  --input_json "$output_path/Unknown/output.json" \
  --output_root "$output_path"

echo "================= Step 4 ================="
python /path/to/evaluation/evaluation/mmmu/main_parse_and_eval.py \
  --path "$output_path" \
  --subject ALL

echo "================= Step 5 ================="
python /path/to/evaluation/evaluation/mmmu/save_scores.py \
  --input_path "$output_path" \
  --output_path "$output_path/scores.csv"

echo "✅ Entire process is complete! The final score has been saved to: $output_path/scores.csv"
