import json
import pandas as pd
import os
import re
import argparse

def extract_choice_robust(response_text):
    response_text = response_text.strip()
    
    matches = re.findall(r'\(([A-Z])\)', response_text, re.IGNORECASE)
    if matches:
        return matches[-1].upper()
        
    matches = re.findall(r'\b([A-Z])\b', response_text, re.IGNORECASE)
    if matches:
        return matches[-1]
        
    return "PARSE_FAILED"

def merge_and_score_definitively(base_dir, input_files, output_csv_file):
    results_data = []

    for filename in input_files:
        filepath = os.path.join(base_dir, filename)
        if not os.path.exists(filepath):
            print(f"⚠️ File doesn't exist,skipping: {filepath}")
            continue
        
        with open(filepath, 'r') as f:
            print(f"processing {filepath}...")
            for line in f:
                record = json.loads(line)
                model_pred_index = extract_choice_robust(record['answer'])
                gt_index = record['gt_answer'].strip().strip('()').upper()
                is_correct = 1 if model_pred_index == gt_index else 0

                results_data.append({
                    'source': record['source'],
                    'result': is_correct,
                    'category': record.get('category', 'Unknown'),
                    'questionId': record.get('questionId', -1)
                })

    df = pd.DataFrame(results_data)
    df.to_csv(output_csv_file, index=False)

    print(f"\n✅  Successfully merge {len(results_data)} data to {output_csv_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge evaluation results and score them.")
    parser.add_argument("--base_dir", type=str, required=True,
                        help="Base directory containing input JSONL files")
    parser.add_argument("--input_files", type=str, nargs='+', required=True,
                        help="List of input JSONL filenames")
    parser.add_argument("--output_csv_file", type=str, required=True,
                        help="Path to the output CSV file")
    args = parser.parse_args()

    merge_and_score_definitively(args.base_dir, args.input_files, args.output_csv_file)
