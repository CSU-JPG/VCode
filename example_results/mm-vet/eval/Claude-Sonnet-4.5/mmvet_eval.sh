#!/bin/bash

set -u
set -o pipefail

PYTHON_EXECUTABLE="python"

INFERENCE_SCRIPT="/path/to/evaluation/mm-vet/run_benchmark_gpt4o-mini_lmms-eval.py"
EVALUATION_SCRIPT="/path/to/evaluation/mm-vet/evaluator.py"

# api gpt4o-mini-2024-0718
API_KEY_INFERENCE="YOUR_API_KEY_HERE"
# api gpt4-0613
API_KEY_EVALUATION="YOUR_API_KEY_HERE"

# workspace base path
BASE_WORKSPACE_PATH="./"

# A list of tasks that need to be executed repeatedly (defined using an array).
mmvet_paths=(
    "./"
)

output_dirs=(
    "gpt4o-mini-inference"
)

BASE_URL="YOUR_BASE_URL_HERE"
MMVET_METADATA="/path/to/data/mm-vet/mm-vet.json"


num_tasks=${#mmvet_paths[@]}
success_count=0
failure_count=0
failed_tasks=()

echo "Automation script starts, with a total of ${num_tasks} tasks to be executed."
echo "The failure of a single task will not interrupt the entire process."
echo "========================================================"

for (( i=0; i<${num_tasks}; i++ )); do

    current_mmvet_path=${mmvet_paths[$i]}
    current_output_dir=${output_dirs[$i]}
    task_num=$((i + 1))
    
    (
        set -e 

        echo ""
        echo "---===[ Start task ${task_num}/${num_tasks}: ${current_output_dir} ]===---"
        echo ""

        echo "--> Step 1: Run the inference..."
        echo "    MM-Vet Path: ${current_mmvet_path}"
        echo "    Output Dir:  ${current_output_dir}"

        ${PYTHON_EXECUTABLE} ${INFERENCE_SCRIPT} \
            --mmvet_path "${current_mmvet_path}" \
            --mmvet_metadata "${MMVET_METADATA}" \
            --base_url "${BASE_URL}" \
            --output_dir "${current_output_dir}" \
            --api_key "${API_KEY_INFERENCE}"

        echo "Inference completed."
        echo ""

        result_path="${BASE_WORKSPACE_PATH}/${current_output_dir}"
        result_file="${result_path}/gpt-4o-mini.json"

        echo "--> Step 2: Run the scoring..."
        echo "    Result Path: ${result_path}"
        echo "    Result File: ${result_file}"
        echo "    MM-Vet Path: ${current_mmvet_path}"

        ${PYTHON_EXECUTABLE} ${EVALUATION_SCRIPT} \
            --mmvet_path "${MMVET_METADATA}" \
            --result_file "${result_file}" \
            --result_path "${result_path}" \
            --base_url "${BASE_URL}" \
            --openai_api_key "${API_KEY_EVALUATION}"

        echo "Scoring completed."

    ) && {
        echo ""
        echo "---===[ Task ${task_num} (${current_output_dir}) executed successfully. ]===---"
        success_count=$((success_count + 1))
    } || {
        echo ""
        echo "---!!! [Error] Task ${task_num} (${current_output_dir}) failed to execute !!!---"
        echo "---!!! Will continue with the next task... !!!---"
        failure_count=$((failure_count + 1))
        failed_tasks+=("${current_output_dir}")
    }
    echo "========================================================"
done

echo ""
echo "All tasks have been completed!"
echo "---------- [ Executive Summary ] ----------"
echo "Total number of tasks: ${num_tasks}"
echo "Success: ${success_count}"
echo "Fail: ${failure_count}"

if [ ${failure_count} -gt 0 ]; then
    echo "Failed Task List:"
    for task in "${failed_tasks[@]}"; do
        echo "  - ${task}"
    done
fi
echo "------------------------------------"

if [ ${failure_count} -gt 0 ]; then
    exit 1
fi
