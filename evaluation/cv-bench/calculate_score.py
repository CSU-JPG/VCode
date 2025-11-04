#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pandas as pd

def calculate_accuracy(df, source):
    source_df = df[df['source'] == source]
    accuracy = source_df['result'].mean() if not source_df.empty else 0.0
    return accuracy

def calculate_subtask_accuracy(df, subtask_category):
    subtask_df = df[df['category'] == subtask_category]
    accuracy = subtask_df['result'].mean() if not subtask_df.empty else 0.0
    count = len(subtask_df)
    return accuracy, count

def main():

    parser = argparse.ArgumentParser(description="Calculate CV-Bench accuracies")
    parser.add_argument("--input_csv", type=str, required=True,
                        help="Path to the input CSV file")
    parser.add_argument("--output_csv", type=str, required=True,
                        help="Path to save the output CSV file")
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv)

    accuracy_2d_ade = calculate_accuracy(df, 'ADE20K')
    accuracy_2d_coco = calculate_accuracy(df, 'COCO')
    accuracy_3d_omni = calculate_accuracy(df, 'Omni3D')
    accuracy_2d = (accuracy_2d_ade + accuracy_2d_coco) / 2
    accuracy_3d = accuracy_3d_omni
    combined_accuracy = (accuracy_2d + accuracy_3d) / 2

    subtask_mapping = {
        'count': "Object Count",
        'spatial': "Spatial Relationship",
        'depth': "Depth Order",
        'relative': "Relative Distance"
    }

    subtask_scores = {}
    for category_name, full_name in subtask_mapping.items():
        accuracy, count = calculate_subtask_accuracy(df, category_name)
        subtask_scores[full_name] = {'accuracy': accuracy, 'count': count}

    results = []

    results.append({"Metric": "CV-Bench Accuracy", "Accuracy": combined_accuracy, "Samples": len(df)})
    results.append({"Metric": "2D Accuracy", "Accuracy": accuracy_2d, "Samples": len(df[df['source'].isin(['ADE20K','COCO'])])})
    results.append({"Metric": "3D Accuracy", "Accuracy": accuracy_3d, "Samples": len(df[df['source']=='Omni3D'])})
    results.append({"Metric": "ADE20K Accuracy", "Accuracy": accuracy_2d_ade, "Samples": len(df[df['source']=='ADE20K'])})
    results.append({"Metric": "COCO Accuracy", "Accuracy": accuracy_2d_coco, "Samples": len(df[df['source']=='COCO'])})
    results.append({"Metric": "Omni3D Accuracy", "Accuracy": accuracy_3d_omni, "Samples": len(df[df['source']=='Omni3D'])})

    for full_name, score_info in subtask_scores.items():
        results.append({"Metric": f"{full_name}", "Accuracy": score_info['accuracy'], "Samples": score_info['count']})

    out_df = pd.DataFrame(results)
    out_df.to_csv(args.output_csv, index=False)

    print(f"✅ Results saved to {args.output_csv}")

if __name__ == "__main__":
    main()
