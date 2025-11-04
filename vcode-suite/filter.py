import os
import re
import argparse

def clean_svg_file(file_path):
    """
    Cleans a single SVG file by keeping only the last valid <svg>...</svg> block
    and escaping standalone '&' characters.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"Error: Could not read file {file_path}: {e}")
        return

    svg_end_pattern = r'</svg>'
    svg_ends = list(re.finditer(svg_end_pattern, content, re.IGNORECASE))
    
    if not svg_ends:
        return
    
    last_svg_end = svg_ends[-1]
    end_pos = last_svg_end.end()
    
    content_before_end = content[:last_svg_end.start()]
    svg_start_pattern = r'<svg[^>]*>'
    svg_starts = list(re.finditer(svg_start_pattern, content_before_end, re.IGNORECASE))
    
    if not svg_starts:
        return
    
    last_svg_start = svg_starts[-1]
    start_pos = last_svg_start.start()
    
    cleaned_content = content[start_pos:end_pos]

    cleaned_content = re.sub(r'&(?!amp;|lt;|gt;|quot;|#)', '&amp;', cleaned_content)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)
    except Exception as e:
        print(f"Error: Could not write to file {file_path}: {e}")

def process_svg_folder(folder_path):
    if not os.path.isdir(folder_path):
        print(f"Error: The provided path '{folder_path}' is not a valid directory.")
        return
    
    print(f"Starting to process folder: {folder_path}")
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith('.svg'):
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, folder_path)
                print(f"  Processing: {relative_path}")
                clean_svg_file(file_path)
                file_count += 1
    
    print(f"\nProcessing complete. Total files handled: {file_count}.")

def main():
    parser = argparse.ArgumentParser(
        description="Recursively cleans all SVG files in a directory by keeping only the last SVG block and fixing entities."
    )
    
    parser.add_argument(
        "--svg-folder",
        required=True,
        help="Path to the target directory containing SVG files."
    )
    
    args = parser.parse_args()
    
    process_svg_folder(args.svg_folder)

if __name__ == "__main__":
    main()