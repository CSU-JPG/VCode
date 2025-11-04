from openai import OpenAI
import base64
import os
import glob
from pathlib import Path
import time
import tiktoken
import sys
import argparse
import re

def get_image_mime_type(image_path):
    extension = Path(image_path).suffix.lower()
    return {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.bmp': 'image/bmp', '.webp': 'image/webp'}.get(extension, 'image/png')

def count_tokens(text):
    """Count tokens using OpenAI's tokenizer"""
    if not text: return 0
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return 0

def generate_image_description(client, model_name, image_path):
    """Generate detailed description of the image"""
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        mime_type = get_image_mime_type(image_path)
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[{ 
                "role": "user", 
                "content": [
                        {
                            "type": "text",
                            "text": """Please provide a detailed and accurate description of this image. Focus on:

1. Main objects, shapes, and elements
2. Colors, textures, and visual properties
3. Spatial relationships and positioning
4. Style and artistic characteristics
5. Any text, symbols, or specific details

Be precise and comprehensive - this description will be used to recreate the image as an SVG. Include geometric details, proportions, and layout information that would be necessary for accurate reproduction."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
            }],
            stream=False, max_tokens=16384
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating description for image {image_path}: {e}")
        return None


def generate_svg_from_description(client, model_name, description):
    """Generate SVG code from text description"""
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": f"""Based on the following description, generate clean and accurate SVG code:

{description}

Requirements:
1. Output ONLY complete SVG code, no explanations or other text
2. Use appropriate dimensions (e.g., viewBox="0 0 400 400" or similar)
3. Include all elements described with accurate colors, shapes, and positioning
4. Use clean, well-structured SVG syntax
5. Ensure the SVG is self-contained and complete
6. Start with <svg viewBox="..." xmlns="http://www.w3.org/2000/svg"> and end with </svg>
7. Use precise geometric shapes and paths where appropriate
8. Match colors and proportions as closely as possible to the description


Generate the SVG now:"""
                }
            ],
            stream=False, max_tokens=16384
        )
        svg_code = response.choices[0].message.content.strip()
        svg_code = re.sub(r'^```svg\s*', '', svg_code, flags=re.MULTILINE)
        svg_code = re.sub(r'^```\s*$', '', svg_code, flags=re.MULTILINE).strip()
        return svg_code
    except Exception as e:
        print(f"Error generating SVG from description: {e}")
        return None

def process_image_to_text_to_svg(client, model_name, image_path):
    """Complete pipeline: image -> text description -> SVG"""
    print(f"Step 1: Generating description for {os.path.basename(image_path)}")
    description = generate_image_description(client, model_name, image_path)
    if not description: return None, None
    
    print(f"  Description generated successfully ({count_tokens(description)} tokens)")
    print(f"  Waiting 3 seconds before generating SVG...")
    time.sleep(3)
    
    print(f"Step 2: Generating SVG from description")
    svg_code = generate_svg_from_description(client, model_name, description)
    if not svg_code: return description, None
    
    print(f"  SVG generated successfully ({count_tokens(svg_code)} tokens)")
    return description, svg_code

def get_image_files(folder_path):
    """Get all image files in the folder recursively"""
    folder = Path(folder_path)
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    image_files = []
    for file_path in folder.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(str(file_path))
    return sorted(image_files)

def extract_image_id(image_path):
    """Extract ID from image path (filename without extension)"""
    return Path(image_path).stem

def batch_process_images(images_folder, svg_output_folder, description_output_folder, client, model_name):
    """Batch process images through the img2text2svg pipeline with aligned directory structure"""
    if not os.path.exists(images_folder):
        print(f"Error: Folder {images_folder} does not exist")
        return
    image_files = get_image_files(images_folder)
    if not image_files:
        print(f"No image files found in folder {images_folder}")
        return
    
    print(f"Found {len(image_files)} image files to process.")
    
    successful_descriptions, successful_svgs, failed_count = 0, 0, 0
    total_description_tokens, total_svg_tokens = 0, 0
    
    for i, image_path in enumerate(image_files, 1):
        rel_path = os.path.relpath(image_path, images_folder)
        print(f"\nProcessing {i}/{len(image_files)} image: {rel_path}")
        
        description, svg_code = process_image_to_text_to_svg(client, model_name, image_path)
        
        if description:
            successful_descriptions += 1
            description_tokens = count_tokens(description)
            total_description_tokens += description_tokens
            
            desc_output_dir = Path(description_output_folder) / Path(rel_path).parent
            desc_output_dir.mkdir(parents=True, exist_ok=True)
            desc_path = desc_output_dir / f"{Path(rel_path).stem}_description.txt"
            
            with open(desc_path, 'w', encoding='utf-8') as f: f.write(description)
            print(f"  → Description saved: {desc_path}")
            
            if svg_code:
                successful_svgs += 1
                svg_tokens = count_tokens(svg_code)
                total_svg_tokens += svg_tokens
                
                svg_output_dir_path = Path(svg_output_folder) / Path(rel_path).parent
                svg_output_dir_path.mkdir(parents=True, exist_ok=True)
                svg_path = svg_output_dir_path / f"{Path(rel_path).stem}.svg"
                
                with open(svg_path, 'w', encoding='utf-8') as f: f.write(svg_code)
                print(f"  → SVG saved: {svg_path}")
            else:
                print(f"⚠ {rel_path} partial success (description only)")
        else:
            failed_count += 1
            print(f"✗ {rel_path} processing failed")
        
        if i < len(image_files): time.sleep(2)
    
    print("\n" + "="*50 + "\nPROCESSING SUMMARY\n" + "="*50)
    print(f"Total images processed: {len(image_files)}")
    print(f"Successful descriptions: {successful_descriptions}, Successful SVGs: {successful_svgs}, Failed: {failed_count}")
    print(f"Total description tokens: {total_description_tokens:,}, Total SVG tokens: {total_svg_tokens:,}")
    print(f"Total tokens used: {(total_description_tokens + total_svg_tokens):,}")
    print(f"Description files saved to: {description_output_folder}")
    print(f"SVG files saved to: {svg_output_folder}")

def main():
    parser = argparse.ArgumentParser(
        description="Batch convert images to SVG via text description using API.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("images_folder", help="Path to the input folder containing images.")
    parser.add_argument("svg_output_folder", help="Path to the output folder to save SVG files.")
    parser.add_argument("--description-output-folder", default="generated_descriptions", help="Path to save image descriptions.")
    parser.add_argument("--model", default="claude-4-opus", help="Model name to use for generation.")
    parser.add_argument("--base-url", default="https://tao.plus7.plus/v1", help="The base URL for the API endpoint.")
    parser.add_argument("--api-key", required=True, help="API key for authentication.")
    
    args = parser.parse_args()

    print("Starting img2text2svg batch processing...")

    client = OpenAI(
        base_url=args.base_url,
        api_key=args.api_key
    )

    batch_process_images(
        images_folder=args.images_folder,
        svg_output_folder=args.svg_output_folder,
        description_output_folder=args.description_output_folder,
        client=client,
        model_name=args.model
    )

    print("\nProcessing completed!")

if __name__ == "__main__":
    main()
