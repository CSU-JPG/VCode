from openai import OpenAI
import base64
import os
from pathlib import Path
import time
import mimetypes
import argparse


def get_image_mime_type(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type and mime_type.startswith('image/'):
        return mime_type

    ext = Path(image_path).suffix.lower()
    ext_to_mime = {
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
        '.gif': 'image/gif', '.bmp': 'image/bmp', '.webp': 'image/webp'
    }
    return ext_to_mime.get(ext, 'image/png')

def find_matching_image(base_folder, relative_svg_path):
    base_folder = Path(base_folder)
    svg_stem = relative_svg_path.stem

    search_dir = base_folder / relative_svg_path.parent
    if not search_dir.is_dir():
        return None
        
    for ext in ['.png', '.jpg', '.jpeg']:
        potential_path = search_dir / f"{svg_stem}{ext}"
        if potential_path.exists():
            return potential_path
    return None

def analyze_visual_differences(original_image_path, rendered_svg_image_path, api_config):
    client = OpenAI(
        base_url=api_config['base_url'],
        api_key=api_config['api_key']
    )
    try:
        original_mime_type = get_image_mime_type(original_image_path)
        rendered_mime_type = get_image_mime_type(rendered_svg_image_path)
        with open(original_image_path, "rb") as f:
            original_base64 = base64.b64encode(f.read()).decode('utf-8')
        with open(rendered_svg_image_path, "rb") as f:
            rendered_base64 = base64.b64encode(f.read()).decode('utf-8')

        prompt = """Compare the original image (first) with the SVG-rendered image (second) and identify SPECIFIC differences for SVG code revision.

Focus on identifying:

1. LOCATION-SPECIFIC DIFFERENCES:
   - Which areas/regions differ (top-left, center, bottom-right, etc.)
   - Missing or extra elements in specific positions

2. VISUAL ATTRIBUTE DIFFERENCES:
   - Color mismatches (specify which elements and what colors)
   - Shape distortions (which shapes are wrong and how)
   - Size/proportion issues (which elements are too big/small)
   - Position/alignment problems

3. SPECIFIC SVG REVISION SUGGESTIONS:
   - Which SVG elements need modification (circles, paths, rects, etc.)
   - What attributes to change (fill, stroke, cx, cy, width, height, d, etc.)
   - Specific color values or coordinate adjustments needed

Format your response as actionable SVG revision instructions."""

        response = client.chat.completions.create(
            model=api_config['model'],
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:{original_mime_type};base64,{original_base64}", "detail": "high"}}, {"type": "image_url", "image_url": {"url": f"data:{rendered_mime_type};base64,{rendered_base64}", "detail": "high"}}]}],
            stream=False,
            max_tokens=api_config['max_tokens']
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in analysis: {e}")
        return None

def visual_feedback_optimize(original_image_path, rendered_svg_image_path, current_svg_code, optimization_goals, api_config):
    client = OpenAI(
        base_url=api_config['base_url'],
        api_key=api_config['api_key']
    )
    try:
        original_mime_type = get_image_mime_type(original_image_path)
        rendered_mime_type = get_image_mime_type(rendered_svg_image_path)
        with open(original_image_path, "rb") as f:
            original_base64 = base64.b64encode(f.read()).decode('utf-8')
        with open(rendered_svg_image_path, "rb") as f:
            rendered_base64 = base64.b64encode(f.read()).decode('utf-8')

        prompt = f"""You are an SVG code specialist. Based on the visual analysis and comparison between the original image and current SVG rendering, make SPECIFIC code modifications to fix identified issues.

VISUAL ANALYSIS FINDINGS:
{optimization_goals}

CURRENT SVG CODE:
{current_svg_code}

INSTRUCTIONS:
1. Analyze the current SVG code structure and elements
2. Based on the visual analysis findings, identify which specific SVG elements need modification
3. Make precise changes to fix the identified issues:
   - Adjust colors (fill, stroke attributes)
   - Fix shapes and paths (modify d attributes, coordinates)
   - Correct sizes and positions (width, height, cx, cy, x, y)
   - Add missing elements or remove incorrect ones
4. Output ONLY the complete revised SVG code
5. Ensure all modifications directly address the issues mentioned in the analysis
6. Start with <svg and end with </svg>

Revised SVG code:"""

        response = client.chat.completions.create(
            model=api_config['model'],
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:{original_mime_type};base64,{original_base64}", "detail": "high"}}, {"type": "image_url", "image_url": {"url": f"data:{rendered_mime_type};base64,{rendered_base64}", "detail": "high"}}]}],
            stream=False,
            max_tokens=api_config['max_tokens']
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in optimization: {e}")
        return None

def batch_optimize_svgs(svg_folder, original_folder, rendered_folder, output_folder, analysis_folder, api_config):
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(analysis_folder, exist_ok=True)

    svg_files = list(Path(svg_folder).rglob("*.svg"))
    if not svg_files:
        print(f"No SVG files found in {svg_folder}")
        return

    print(f"🚀 Starting optimization for {len(svg_files)} SVG files")
    print("=" * 50)
    successful = 0
    failed = 0

    for i, svg_file in enumerate(svg_files, 1):
        relative_path = svg_file.relative_to(svg_folder)
        print(f"\n[{i}/{len(svg_files)}] Processing: {relative_path}")

        original_path = find_matching_image(original_folder, relative_path)
        rendered_path = find_matching_image(rendered_folder, relative_path)

        if not original_path or not original_path.exists():
            print(f"  ❌ Original image not found for {relative_path}")
            failed += 1
            continue
        if not rendered_path or not rendered_path.exists():
            print(f"  ❌ Rendered image not found for {relative_path}")
            failed += 1
            continue

        print(f"  ✓ Found original: {original_path}")
        print(f"  ✓ Found rendered: {rendered_path}")

        try:
            with open(svg_file, 'r', encoding='utf-8') as f:
                current_svg = f.read()
        except Exception as e:
            print(f"  ❌ Error reading SVG: {e}")
            failed += 1
            continue

        print(f"  📊 Analyzing visual differences...")
        analysis = analyze_visual_differences(str(original_path), str(rendered_path), api_config)
        if not analysis:
            analysis = "improve overall accuracy"

        output_subdir = Path(output_folder) / relative_path.parent
        analysis_subdir = Path(analysis_folder) / relative_path.parent
        os.makedirs(output_subdir, exist_ok=True)
        os.makedirs(analysis_subdir, exist_ok=True)

        analysis_file = analysis_subdir / f"{svg_file.stem}_analysis.txt"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write(analysis)
        print(f"  💾 Analysis saved: {analysis_file}")

        print(f"  🔧 Optimizing SVG...")
        optimized_svg = visual_feedback_optimize(str(original_path), str(rendered_path), current_svg, analysis, api_config)

        if optimized_svg:
            output_path = output_subdir / f"{svg_file.stem}_optimized.svg"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(optimized_svg)
            print(f"  ✅ Optimized and saved to: {output_path}")
            successful += 1
        else:
            print(f"  ❌ Optimization failed")
            failed += 1

        if i < len(svg_files):
            time.sleep(2)

    print(f"\n🎯 OPTIMIZATION COMPLETED")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")


def main():
    parser = argparse.ArgumentParser(description="Recursively optimizes SVG files using visual feedback.")
    parser.add_argument('--svg-folder', required=True, help='Root directory of SVG files to process.')
    parser.add_argument('--original-folder', required=True, help='Root directory of original reference images.')
    parser.add_argument('--rendered-folder', required=True, help='Root directory of rendered images from SVGs.')
    parser.add_argument('--output-folder', required=True, help='Directory to save optimized SVGs.')
    parser.add_argument('--analysis-folder', required=True, help='Directory to save analysis reports.')
    
    parser.add_argument('--base-url', type=str, default='https://tao.plus7.plus/v1', help='The base URL for the API endpoint.')
    parser.add_argument('--api-key', type=str, default=os.getenv('OPENAI_API_KEY'), help='API key.')
    parser.add_argument('--model', type=str, default='claude-4-opus', help='The model to use.')
    parser.add_argument('--max-tokens', type=int, default=16384, help='Max tokens for the response.')
    
    args = parser.parse_args()

    if not args.api_key:
        parser.error("API key is required. Provide it via --api-key or set OPENAI_API_KEY environment variable.")
        
    api_config = {
        'base_url': args.base_url,
        'api_key': args.api_key,
        'model': args.model,
        'max_tokens': args.max_tokens
    }

    batch_optimize_svgs(
        svg_folder=args.svg_folder,
        original_folder=args.original_folder,
        rendered_folder=args.rendered_folder,
        output_folder=args.output_folder,
        analysis_folder=args.analysis_folder,
        api_config=api_config
    )

if __name__ == "__main__":
    main()