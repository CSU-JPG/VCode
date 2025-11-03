# img2svg.py
from openai import OpenAI
import base64
import os
import glob
from pathlib import Path
import time
import re
import sys
import argparse

def clean_svg_output(svg_content):
    """Clean SVG output by removing code block markers and fixing common issues"""
    if not svg_content:
        return None

    svg_content = re.sub(r'^```svg\s*', '', svg_content, flags=re.MULTILINE)
    svg_content = re.sub(r'^```\s*$', '', svg_content, flags=re.MULTILINE)
    svg_content = re.sub(r'```$', '', svg_content)
    svg_content = svg_content.strip()
    
    if not svg_content.startswith('<svg'):
        svg_match = re.search(r'<svg[^>]*>', svg_content)
        if svg_match:
            svg_content = svg_content[svg_match.start():]
    
    if not svg_content.endswith('</svg>'):
        last_svg_end = svg_content.rfind('</svg>')
        if last_svg_end != -1:
            svg_content = svg_content[:last_svg_end + 6]
    
    return svg_content if svg_content.startswith('<svg') and svg_content.endswith('</svg>') else None

def get_image_mime_type(image_path):
    extension = Path(image_path).suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp'
    }
    return mime_types.get(extension, 'image/png')

def quick_generate_svg(client, model_name, image_path, max_tokens=16384):
    """Quick function to generate SVG"""
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        mime_type = get_image_mime_type(image_path)
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user","content": [
                {"type": "image_url",
                 "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
                {"type": "text", "text": """Convert this image to SVG code. Follow these rules:

CRITICAL REQUIREMENTS:
- Output only pure SVG code, no markdown blocks or explanations  
- Start with <svg viewBox="..." xmlns="http://www.w3.org/2000/svg"> and end with </svg>
- Use only native SVG elements (no external images or links)
- Include viewBox to ensure all elements are visible and auto-scale properly
- Calculate appropriate viewBox dimensions to contain all content with some padding

Generate the SVG now:"""},
                ]}],
                stream=False,
                max_tokens=max_tokens
        )
        
        raw_content = response.choices[0].message.content.strip()
        cleaned_svg = clean_svg_output(raw_content)
        
        return cleaned_svg
        
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

def get_image_files(folder_path):
    """Get all image files in the folder recursively"""
    folder = Path(folder_path)
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    image_files = []

    for file_path in folder.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(str(file_path))
    
    return sorted(image_files)

def batch_process_images(images_folder, svg_output_folder, client, model_name, sleep_duration, max_tokens=16384):
    """Batch process images and save SVG files with aligned directory structure"""
    
    if not os.path.exists(images_folder):
        print(f"Error: Folder {images_folder} does not exist")
        return
    
    image_files = get_image_files(images_folder)
    
    if not image_files:
        print(f"No image files found in folder {images_folder}")
        return
    
    print(f"Found {len(image_files)} image files to process in '{images_folder}'")
    
    successful_count = 0
    failed_count = 0
    
    for i, image_path in enumerate(image_files, 1):
        rel_path = os.path.relpath(image_path, images_folder)
        print(f"Processing {i}/{len(image_files)} image: {rel_path}")

        svg_code = quick_generate_svg(client, model_name, image_path, max_tokens=max_tokens)
        
        if svg_code:
            svg_rel_dir = os.path.dirname(rel_path)
            svg_output_dir = os.path.join(svg_output_folder, svg_rel_dir) if svg_rel_dir else svg_output_folder
            os.makedirs(svg_output_dir, exist_ok=True)
            
            svg_filename = f"{Path(rel_path).stem}.svg"
            svg_path = os.path.join(svg_output_dir, svg_filename)
            
            try:
                with open(svg_path, 'w', encoding='utf-8') as f:
                    f.write(svg_code)
                print(f"  → SVG saved: {svg_path}")
                successful_count += 1
            except Exception as e:
                print(f"  ✗ Error saving SVG: {e}")
                failed_count += 1
        else:
            failed_count += 1
            print(f"✗ {rel_path} processing failed")
        
        if i < len(image_files):
            time.sleep(sleep_duration)
    
    print(f"\nProcessing completed: {successful_count} successful, {failed_count} failed")

def main():
    parser = argparse.ArgumentParser(description="Batch convert images to SVG using an AI model.")

    parser.add_argument("images_folder", help="Path to the input folder containing images.")
    parser.add_argument("svg_output_folder", help="Path to the output folder to save SVG files.")
    
    parser.add_argument(
        "--model", 
        default="Qwen/Qwen3-VL-235B-A22B-Instruct", 
        help="The model name to use for conversion."
    )
    parser.add_argument(
        "--base-url", 
        default="https://api.deepinfra.com/v1/openai", 
        help="The base URL for the API endpoint."
    )
    parser.add_argument(
        "--api-key", 
        required=True,
        help="API key for the service. This argument is required."
    )
    parser.add_argument(
        "--sleep", 
        type=int, 
        default=5, 
        help="Seconds to wait between API calls."
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=16384,
        help="Maximum tokens for the model response."
    )
    
    args = parser.parse_args()

    if not args.api_key:
        print("Error: API key not found. Please set the DEEPINFRA_API_KEY environment variable or use the --api-key argument.")
        sys.exit(1)

    client = OpenAI(
        base_url=args.base_url,
        api_key=args.api_key
    )

    print("Starting batch image processing...")
    batch_process_images(
        images_folder=args.images_folder,
        svg_output_folder=args.svg_output_folder,
        client=client,
        model_name=args.model,
        sleep_duration=args.sleep,
        max_tokens=args.max_tokens
    )
    print(f"\nProcessing completed!")
    print(f"SVG files saved to: {args.svg_output_folder} (with aligned directory structure)")

if __name__ == "__main__":
    main()
