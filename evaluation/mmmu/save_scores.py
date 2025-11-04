# Beautiful table to print results of all categories

import os
import csv
from typing import Dict
import json
import numpy as np
from tabulate import tabulate

from argparse import ArgumentParser

from utils.data_utils import CAT_SHORT2LONG, DOMAIN_CAT2SUB_CAT
from utils.eval_utils import calculate_ins_level_acc

def main():
    parser = ArgumentParser()
    parser.add_argument('--input_path', type=str, default="./example_outputs/blip2_flant5xxl", help="The path to the input directory containing model outputs.")
    parser.add_argument('--output_path', type=str, default=None, help="The path to save the results as a CSV file. If not provided, results are only printed to the console.")
    args = parser.parse_args()

    # load all results
    all_results = {}
    for cat_folder_name in os.listdir(args.input_path):
        if cat_folder_name in CAT_SHORT2LONG.values():
            cat_folder_path = os.path.join(args.input_path, cat_folder_name)
            result_path = os.path.join(cat_folder_path, 'result.json')
            if os.path.exists(result_path):
                cat_results = json.load(open(result_path))
                all_results[cat_folder_name] = cat_results

    headers = ['Subject', 'Data Num', 'Acc']
    table = []

    # add domain Subject
    for domain, in_domain_cats in DOMAIN_CAT2SUB_CAT.items():
        in_domain_cat_results = {}
        for cat_name in in_domain_cats:
            if cat_name in all_results.keys():
                in_domain_cat_results[cat_name] = all_results[cat_name]
        
        if not in_domain_cat_results:
            continue
            
        in_domain_ins_acc = calculate_ins_level_acc(in_domain_cat_results)
        in_domain_data_num = np.sum([cat_results['num_example'] for cat_results in in_domain_cat_results.values()])
        table.append(['Overall-' + domain, int(in_domain_data_num), round(in_domain_ins_acc, 3)])
        # add sub category
        for cat_name, cat_results in in_domain_cat_results.items():
            table.append([cat_name, int(cat_results['num_example']), round(cat_results['acc'], 3)])

    if all_results:
        all_ins_acc = calculate_ins_level_acc(all_results)
        total_data_num = np.sum([cat_results['num_example'] for cat_results in all_results.values()])
        table.append(['Overall', int(total_data_num), round(all_ins_acc, 3)])

    print("--- Evaluation Results ---")
    print(tabulate(table, headers=headers, tablefmt='orgtbl'))
    print("--------------------------\n")

    if args.output_path:
        try:
            output_dir = os.path.dirname(args.output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
            with open(args.output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(table)
            print(f"[+] Results have been successfully saved to: {args.output_path}")
        except IOError as e:
            print(f"[!] Error: Failed to save results to {args.output_path}. Reason: {e}")

if __name__ == '__main__':
    main()