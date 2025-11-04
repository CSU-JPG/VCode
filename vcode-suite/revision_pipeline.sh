#!/bin/bash

# ==============================================================================
#      🚀 AUTOMATED SVG OPTIMIZATION PIPELINE (PYTHON-DRIVEN RECURSION)
# ==============================================================================
#
# This script relies on the Python scripts to handle recursive directory traversal.
# The shell script acts as a high-level orchestrator for the retry logic.
#
# ========================== CONFIGURATION =====================================

# --- Python Script Paths ---
REVISION_SCRIPT="/path/to/revision.py"
FILTER_SCRIPT="/path/to/filter.py"
RENDER_SCRIPT="/path/to/svg_render_img.py"

# --- Pipeline Control ---
MAX_LOOPS=5

# --- Workspace Configuration ---
WORKSPACE_DIR="./missing_revision_temp"

# --- Input Folders (Initial State) ---
INITIAL_SVG_FOLDER="./generated_svgs"
ORIGINAL_IMAGES_FOLDER="/path/to/images-folder"
INITIAL_RENDERED_FOLDER="./generated_imgs"

# --- Final Output Folders ---
FINAL_OPTIMIZED_SVGS_FOLDER="./optimized_svgs"
FINAL_ANALYSIS_FOLDER="./visual_analysis"
FINAL_RENDERED_IMGS_FOLDER="./optimized_imgs"

# --- API Configuration ---
API_KEY="YOUR_API_KEY_HERE"
BASE_URL="YOUR_BASE_URL_HERE"
MODEL="YOUR_MODEL_NAME_HERE"

# ======================= SCRIPT EXECUTION (DO NOT EDIT) =======================

# --- 0. Initialization: Replicate Input Structure in Workspace ---
echo "Preparing a clean workspace at '$WORKSPACE_DIR' with original directory structure..."
rm -rf "$WORKSPACE_DIR"
mkdir -p "$WORKSPACE_DIR"

# Copy contents while preserving structure
cp -a "$INITIAL_SVG_FOLDER/." "$WORKSPACE_DIR/" 2>/dev/null || true
cp -a "$INITIAL_RENDERED_FOLDER/." "$WORKSPACE_DIR/" 2>/dev/null || true

# Prepare final output directories
mkdir -p "$FINAL_OPTIMIZED_SVGS_FOLDER" "$FINAL_ANALYSIS_FOLDER"

echo "🚀 Starting SVG Optimization Pipeline. Max loops: $MAX_LOOPS"
echo "======================================================================"

# --- Main Loop ---
for (( i=1; i<=$MAX_LOOPS; i++ )); do
    # Check if there are any svg files left in the entire workspace tree
    if ! find "$WORKSPACE_DIR" -type f -name "*.svg" -print -quit | grep -q .; then
        echo -e "\n🎉 Success! The workspace is empty. All files processed."
        break
    fi
    NUM_FILES=$(find "$WORKSPACE_DIR" -type f -name "*.svg" | wc -l)

    echo -e "\n🌀 Starting Loop $i/$MAX_LOOPS: Processing $NUM_FILES remaining files..."
    echo "----------------------------------------------------------------"

    # Temporary directories for this loop's aggregated results
    REVISED_DIR_LOOP="$WORKSPACE_DIR/revised_loop_outputs"
    ANALYSIS_DIR_LOOP="$WORKSPACE_DIR/analysis_loop_outputs"
    mkdir -p "$REVISED_DIR_LOOP" "$ANALYSIS_DIR_LOOP"

    # --- Step 1: Revision (Single call, Python handles recursion) ---
    echo "   [1/3] Running Revision recursively on the entire workspace..."
    python "$REVISION_SCRIPT" \
        --api-key "$API_KEY" \
        --base-url "$BASE_URL" \
        --model "$MODEL" \
        --svg-folder "$WORKSPACE_DIR" \
        --original-folder "$ORIGINAL_IMAGES_FOLDER" \
        --rendered-folder "$WORKSPACE_DIR" \
        --output-folder "$REVISED_DIR_LOOP" \
        --analysis-folder "$ANALYSIS_DIR_LOOP"

    # --- Step 2: Filter ---
    echo -e "\n   [2/3] Cleaning all successfully revised SVGs (recursively)..."
    python "$FILTER_SCRIPT" --svg-folder "$REVISED_DIR_LOOP"

    # --- Step 3: Sorting and Moving ---
    echo -e "\n   [3/3] Sorting results and updating workspace..."
    SUCCESS_COUNT=0
    
    find "$REVISED_DIR_LOOP" -type f -name "*_optimized.svg" | while read -r optimized_svg_path; do
        ((SUCCESS_COUNT++))
        relative_optimized_path="${optimized_svg_path#$REVISED_DIR_LOOP/}"
        original_relative_path=$(echo "$relative_optimized_path" | sed 's/_optimized\.svg/\.svg/')
        original_relative_stem="${original_relative_path%.*}"
        
        final_svg_path="$FINAL_OPTIMIZED_SVGS_FOLDER/$original_relative_path"
        final_analysis_path="$FINAL_ANALYSIS_FOLDER/${original_relative_stem}_analysis.txt"
        
        mkdir -p "$(dirname "$final_svg_path")"
        mkdir -p "$(dirname "$final_analysis_path")"
        
        mv "$optimized_svg_path" "$final_svg_path"
        mv "$ANALYSIS_DIR_LOOP/${original_relative_stem}_analysis.txt" "$final_analysis_path" 2>/dev/null || true
        
        rm "$WORKSPACE_DIR/$original_relative_path"
        find "$WORKSPACE_DIR/${original_relative_stem%/*}" -maxdepth 1 -name "${original_relative_stem##*/}*" -not -name "*.svg" -exec rm {} \;
    done

    FAILURE_COUNT=$((NUM_FILES - SUCCESS_COUNT))
    echo "   -> Loop $i Summary: $SUCCESS_COUNT succeeded, $FAILURE_COUNT failed and will be retried."

    rm -rf "$REVISED_DIR_LOOP" "$ANALYSIS_DIR_LOOP"

    if [[ $i -eq $MAX_LOOPS ]]; then
        echo -e "\n🏁 Pipeline finished after reaching the maximum of $MAX_LOOPS loops."
    fi
done

# --- Final Rendering Step ---
echo -e "\n🎨 Rendering final optimized SVGs to images..."
if [ -n "$(ls -A $FINAL_OPTIMIZED_SVGS_FOLDER 2>/dev/null)" ]; then
    python "$RENDER_SCRIPT" \
        --svg-input-dir "$FINAL_OPTIMIZED_SVGS_FOLDER" \
        --image-output-dir "$FINAL_RENDERED_IMGS_FOLDER" \
        --reference-dir "$ORIGINAL_IMAGES_FOLDER"
else
    echo "   -> No SVGs to render, skipping."
fi


# --- Final Report ---
echo -e "\n✅ Pipeline complete."
echo "   Final successful results are in:"
echo "   - Optimized SVGs: $FINAL_OPTIMIZED_SVGS_FOLDER"
echo "   - Analysis Reports: $FINAL_ANALYSIS_FOLDER"
echo "   - Rendered Images: $FINAL_RENDERED_IMGS_FOLDER"
echo ""
echo "   Please check the '$WORKSPACE_DIR' directory for any files that failed to process."
echo "   (The workspace maintains the original directory structure.)"