from openai import OpenAI
import base64
import os
from pathlib import Path
import time
import re
import sys
import argparse
import tiktoken

def get_image_mime_type(image_path):
    extension = Path(image_path).suffix.lower()
    return {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.bmp': 'image/bmp', '.webp': 'image/webp'}.get(extension, 'image/png')

def clean_svg_output(svg_content):
    if not svg_content: return None
    svg_content = re.sub(r'^```svg\s*', '', svg_content, flags=re.MULTILINE)
    svg_content = re.sub(r'^```\s*$', '', svg_content, flags=re.MULTILINE).strip()
    if not svg_content.startswith('<svg'):
        svg_match = re.search(r'<svg[^>]*>', svg_content)
        if svg_match: svg_content = svg_content[svg_match.start():]
    if not svg_content.endswith('</svg>'):
        last_svg_end = svg_content.rfind('</svg>')
        if last_svg_end != -1: svg_content = svg_content[:last_svg_end + 6]
    return svg_content if svg_content.startswith('<svg') and svg_content.endswith('</svg>') else None

def generate_svg_with_thinking(client, model_name, image_path, max_tokens):
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
                            "text": """Let's analyze this image and create an SVG representation through a structured thinking process.

Step-by-step analysis:
1. Visual Decomposition
- What are the main visual elements?
- What geometric shapes can be identified?
- What are the key colors and their relationships?

2. Structural Analysis
- How are elements arranged and layered?
- What are the proportions and spatial relationships?
- Are there any repeating patterns or symmetry?

3. SVG Implementation Strategy
- Which SVG elements best represent each component?
- What's the optimal drawing order?
- How to handle complex shapes and gradients?

4. Technical Considerations
- What viewport dimensions are appropriate?
- How to ensure scalability and responsiveness?
- What optimizations can be applied?

After your analysis, provide:
1. Your complete reasoning process
2. The final SVG code implementation

Requirements for SVG output:
- Must be complete and self-contained
- Include all necessary attributes and elements
- Start with <svg tag and end with </svg>
- Use appropriate viewBox and dimensions
- Output only pure SVG code in the final implementation, no markdown blocks

Please proceed with the analysis and generation:"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                ]
            }],
            stream=False,
            max_tokens=max_tokens
        )        
        full_response = response.choices[0].message.content.strip()
        
        if '<svg' in full_response:
            svg_start = full_response.rfind('<svg')
            thinking_process = full_response[:svg_start].strip()
            svg_code = full_response[svg_start:]
            return {'thinking_process': thinking_process, 'svg_code': clean_svg_output(svg_code)}
        else:
            return {'thinking_process': full_response, 'svg_code': None}
        
    except Exception as e:
        print(f"  ✗ Error: {e}", flush=True)
        return None

def process_image_with_thinking(client, model_name, image_path, max_tokens):
    result = generate_svg_with_thinking(client, model_name, image_path, max_tokens)
    if not result:
        return None, None
    return result.get('thinking_process'), result.get('svg_code')

def get_image_files(folder_path):
    folder = Path(folder_path)
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    return sorted([str(p) for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in image_extensions])

def extract_image_id(image_path):
    return Path(image_path).stem


def batch_process_images(images_folder, svg_output_folder, thinking_output_folder, client, model_name, sleep_duration, max_tokens):

    image_files = get_image_files(images_folder)
    if not image_files:
        print(f"No image file in {images_folder} ")
        return
    print(f"Found {len(image_files)} image files to process in '{images_folder}'")

    os.makedirs(svg_output_folder, exist_ok=True)
    os.makedirs(thinking_output_folder, exist_ok=True)

    for i, image_path in enumerate(image_files, 1):
        rel_path = os.path.relpath(image_path, images_folder)
        print(f"\nProcessing {i}/{len(image_files)}: {rel_path}", flush=True)
        
        thinking_process, svg_code = process_image_with_thinking(client, model_name, image_path, max_tokens)
        
        base_rel_path = os.path.splitext(rel_path)[0]
        
        if thinking_process:
            thinking_path = os.path.join(thinking_output_folder, f"{base_rel_path}_thinking.txt")
            os.makedirs(os.path.dirname(thinking_path), exist_ok=True)
            with open(thinking_path, 'w', encoding='utf-8') as f: f.write(thinking_process)
            print(f"  → thinking process is saved: {thinking_path}", flush=True)

        if svg_code:
            svg_path = os.path.join(svg_output_folder, f"{base_rel_path}.svg")
            os.makedirs(os.path.dirname(svg_path), exist_ok=True)
            with open(svg_path, 'w', encoding='utf-8') as f: f.write(svg_code)
            print(f"  → SVG file is saved: {svg_path}", flush=True)
        
        if not thinking_process and not svg_code:
            print(f"✗ {Path(image_path).name} generation failed", flush=True)

        if i < len(image_files):
            time.sleep(sleep_duration)

    print(f"\n✅ Batch processing completed.")
    print(f"SVG files are saved: {svg_output_folder}")
    print(f"Thinking processes are saved: {thinking_output_folder}")

def main():
    parser = argparse.ArgumentParser(description="Batch convert images to SVG via text description using API.")
    

    parser.add_argument("images_folder", help="Path to the input folder containing images.")
    parser.add_argument("svg_output_folder", help="Path to the output folder to save SVG files.")
    
    parser.add_argument(
        "--thinking-folder",
        default="./thinking_process",
        help="Path to save the thinking process text files."
    )
    
    parser.add_argument("--model", default="claude-4-opus-thinking", help="Model name to use for generation.")
    parser.add_argument("--base-url", default="https://tao.plus7.plus/v1", help="The base URL for the API endpoint.")
    parser.add_argument("--api-key", required=True, help="API key for authentication.")
    parser.add_argument("--sleep", type=int, default=5, help="Sleep duration (in seconds) between requests.")
    parser.add_argument("--max-tokens", type=int, default=16384, help="Maximum tokens for generation.")
    args = parser.parse_args()

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    batch_process_images(
        images_folder=args.images_folder,
        svg_output_folder=args.svg_output_folder,
        thinking_output_folder=args.thinking_folder,
        client=client,
        model_name=args.model,
        sleep_duration=args.sleep,
        max_tokens=args.max_tokens
    )

if __name__ == "__main__":
    main()