import base64
import os
import json
from pathlib import Path
import time
import tiktoken
import re
import cv2
import numpy as np
from simplification.cutil import simplify_coords
from openai import OpenAI
from typing import Dict, List, Optional, Tuple
import argparse

def count_tokens(text: str) -> int:
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except:
        return max(1, len(text) // 4)

def clean_svg_output(svg_content: str) -> Optional[str]:
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

def get_image_mime_type(image_path: str) -> str:
    ext = Path(image_path).suffix.lower()
    return {
        '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.gif': 'image/gif', '.bmp': 'image/bmp', '.webp': 'image/webp'
    }.get(ext, 'image/png')

def get_image_size(image_path: str) -> Tuple[int, int]:
    try:
        img = cv2.imread(str(image_path))
        if img is not None:
            h, w = img.shape[:2]
            return int(w), int(h)
    except:
        pass
    return 1024, 768

def extract_image_id(image_path: str) -> str:
    return Path(image_path).stem

def get_image_files(folder_path: str) -> List[str]:
    folder = Path(folder_path)
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    image_files = []
    for file_path in folder.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(str(file_path))
    return sorted(image_files)

class MetadataLoader:
    def __init__(self, args):
        self.args = args

    def load_ocr_data(self, image_id: str) -> List[Dict]:
        if not self.args.ocr_metadata_txt or not os.path.exists(self.args.ocr_metadata_txt):
            return []
        ocr_map = {}
        try:
            with open(self.args.ocr_metadata_txt, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or "\t" not in line: continue
                    fname, json_str = line.split("\t", 1)
                    stem = Path(fname).stem
                    try:
                        arr = json.loads(json_str)
                        if isinstance(arr, list): ocr_map[stem] = arr
                    except: continue
        except: return []
        raw_items = ocr_map.get(image_id, [])
        if not raw_items:
            for key in ocr_map.keys():
                if key.endswith(image_id):
                    raw_items = ocr_map[key]
                    break
        processed = []
        for item in raw_items:
            if not isinstance(item, dict): continue
            text = item.get("transcription", "")
            points = item.get("points", [])
            score = item.get("score", 0.0)
            if not points or len(points) < 4: continue
            quad = [(int(round(p[0])), int(round(p[1]))) for p in points[:4]]
            processed.append({"text": text[:self.args.max_text_len] if isinstance(text, str) else "", "confidence": round(float(score), 2), "quad": quad})
        def sort_key(item):
            xs, ys = zip(*item["quad"])
            area = (max(xs) - min(xs)) * (max(ys) - min(ys))
            return (-item["confidence"], area)
        processed.sort(key=sort_key)
        return processed[:self.args.max_text_items]

    def simplify_polygon(self, points: List[List[float]]) -> Optional[str]:
        if len(points) < 3: return None
        if len(points) < 4:
            int_points = [(int(round(p[0])), int(round(p[1]))) for p in points]
            return "M " + " L ".join(f"{p[0]},{p[1]}" for p in int_points) + " Z"
        try:
            contour = np.array(points, dtype=np.float32).reshape((-1, 1, 2))
            original_area = cv2.contourArea(contour)
            if original_area == 0:
                if len(points) <= 15:
                    int_points = [(int(round(p[0])), int(round(p[1]))) for p in points]
                    return "M " + " L ".join(f"{p[0]},{p[1]}" for p in int_points) + " Z"
                indices = np.round(np.linspace(0, len(points) - 1, 15)).astype(int)
                sampled = [points[i] for i in indices]
                int_points = [(int(round(p[0])), int(round(p[1]))) for p in sampled]
                return "M " + " L ".join(f"{p[0]},{p[1]}" for p in int_points) + " Z"
            if not self.args.simplify_polygons:
                int_points = [(int(round(p[0])), int(round(p[1]))) for p in points]
                return "M " + " L ".join(f"{p[0]},{p[1]}" for p in int_points) + " Z"
            points_np = np.array(points)
            low_eps, high_eps = 0.0, np.sqrt(np.ptp(points_np[:, 0])**2 + np.ptp(points_np[:, 1])**2)
            best_points = points_np
            for _ in range(20):
                mid_eps = (low_eps + high_eps) / 2
                if abs(mid_eps - low_eps) < 1e-6: break
                try:
                    simplified = simplify_coords(points_np, mid_eps)
                    simplified_contour = np.array(simplified, dtype=np.float32).reshape((-1, 1, 2))
                    simplified_area = cv2.contourArea(simplified_contour)
                    area_loss = 1.0 - (simplified_area / original_area)
                    if abs(area_loss) > self.args.simplification_max_area_loss:
                        high_eps = mid_eps
                    else:
                        low_eps = mid_eps
                        best_points = simplified
                except: high_eps = mid_eps
            int_points = [(int(round(p[0])), int(round(p[1]))) for p in best_points]
            return "M " + " L ".join(f"{p[0]},{p[1]}" for p in int_points) + " Z"
        except:
            int_points = [(int(round(p[0])), int(round(p[1]))) for p in points]
            return "M " + " L ".join(f"{p[0]},{p[1]}" for p in int_points) + " Z"

    def load_gsam_data(self, image_path: str, image_id: str) -> List[Dict]:
        if not self.args.gsam_metadata_folder or not os.path.exists(self.args.gsam_metadata_folder):
            return []
        rel_dir = Path(image_path).parent.name
        candidates = [
            Path(self.args.gsam_metadata_folder) / f"{image_id}_metadata.json",
            Path(self.args.gsam_metadata_folder) / f"{image_id}.json",
        ]
        if rel_dir and rel_dir not in (".", "/"):
            candidates.extend([
                Path(self.args.gsam_metadata_folder) / rel_dir / f"{image_id}_metadata.json",
                Path(self.args.gsam_metadata_folder) / rel_dir / f"{image_id}.json",
                Path(self.args.gsam_metadata_folder) / f"{rel_dir}_{image_id}_metadata.json",
                Path(self.args.gsam_metadata_folder) / f"{rel_dir}_{image_id}.json",
            ])
        metadata = None
        for candidate in candidates:
            if candidate.exists():
                try:
                    with open(candidate, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    break
                except: continue
        if not metadata: return []
        detections = []
        if isinstance(metadata, dict):
            if 'detections' in metadata and isinstance(metadata['detections'], list):
                detections = metadata['detections']
            else:
                detections = [v for v in metadata.values() if isinstance(v, dict) and ('label' in v or 'name' in v)]
        elif isinstance(metadata, list):
            detections = metadata
        processed = []
        for det in detections:
            if not isinstance(det, dict): continue
            label = det.get('label') or det.get('name') or ''
            conf = det.get('conf') or det.get('confidence') or det.get('confidence_score', 0.0)
            bbox = det.get('box_xyxy') or det.get('bbox') or det.get('box')
            if bbox and len(bbox) == 4:
                x1, y1, x2, y2 = map(float, bbox)
            elif all(k in det for k in ['x','y','w','h']):
                x1, y1 = float(det['x']), float(det['y'])
                x2, y2 = x1 + float(det['w']), y1 + float(det['h'])
            else: x1 = y1 = x2 = y2 = None
            svg_path = None
            if det.get('polygon_points'):
                svg_path = self.simplify_polygon(det['polygon_points'])
            if not svg_path:
                svg_path = det.get('svg_path')
            item = {"label": str(label), "confidence": round(float(conf), 2)}
            if x1 is not None:
                item["bbox"] = [int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))]
            if svg_path: item["svg_path"] = svg_path
            if 'layer' in det: item["layer"] = det['layer']
            processed.append(item)
        def priority(item):
            label_lower = item["label"].lower()
            face_bonus = 1 if any(k in label_lower for k in ['face','eye','nose','mouth','head']) else 0
            text_bonus = 1 if any(k in label_lower for k in ['text','word','letter','sign','logo']) else 0
            bbox = item.get("bbox")
            area = (bbox[2]-bbox[0])*(bbox[3]-bbox[1]) if bbox else 1e12
            return (-item["confidence"], -(face_bonus + text_bonus), area)
        processed.sort(key=priority)
        return processed


class SVGGenerator:
    def __init__(self, args):
        self.args = args
        self.client = OpenAI(base_url=self.args.base_url, api_key=self.args.api_key)
        self.loader = MetadataLoader(self.args)

    def build_prompt(self, W: int, H: int, ocr_data: List[Dict], gsam_data: List[Dict]) -> Tuple[str, str]:

        system_prompt = f"""You are a helpful assistant that converts images into clean, complete SVG vector graphics.

Your primary task is img2svg conversion for Visual Question Answering. You have access to two types of metadata to assist with precision:

METADATA AVAILABLE:
- OCR metadata: Text regions with precise 4-point quadrilaterals for accurate text placement
- Object detection metadata: Object boundaries with labels, confidence scores, and svg_path outlines

SPECIAL CASE HANDLING (Hint Strategy):
Sometimes, an image may depict a person, character, or artwork where fine details like facial features or texture could be lost during vectorization. Examples include:
- A recognizable public figure such as a scientist or political leader  
- A well-known fictional character from popular culture
- A famous painting or portrait by a specific artist

If the subject in the image is of this nature and important identity cues might be lost:
- Preserve recognizability by including visual hints such as characteristic clothing, accessories, environment, or symbolic elements
- When confident, you may add a <text> element near the subject that provides:
  • Their commonly known name
  • The name of the associated work or series  
  • The title or creator of an artwork

If the subject does not fit these examples or is not clearly recognizable:
- Generate a clean SVG with no extra text labels
- Focus on accurate shapes, proportions, and composition

METADATA INTEGRATION:
1) Text rendering: Use OCR quadrilaterals as authoritative coordinates for text placement. Render literal text strings with appropriate transforms for rotation/skew.
2) Object boundaries: Use detection svg_paths as authoritative contours. Infer fill/stroke colors and add internal details within these boundaries.
3) Background reconstruction: Fill in unlabeled regions using native SVG primitives.

PROCESSING PRIORITY:
1. Use provided metadata for precise positioning (OCR quads, detection paths)
2. Apply hint strategy for recognizable subjects  
3. Reconstruct missing background/unlabeled areas
4. Ensure proper layering and visual completeness

OUTPUT REQUIREMENTS:
- Output only pure SVG code, no markdown blocks or explanations
- Start with <svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"> and end with </svg>
- Use only native SVG elements (no external images or links)  
- Include viewBox to ensure all elements are visible and auto-scale properly
- Do not include explanations or commentary

This SVG will be used in a Visual Question Answering task, so ensure the output retains as much semantic identity as possible when visual details are reduced."""
        user_prompt = f"Image dimensions: {W}x{H}\n\n"
        metadata = {"image_size": {"w": W, "h": H}, "objects": []}
        obj_id = 0
        for ocr_item in ocr_data:
            metadata["objects"].append({"id": obj_id, "type": "text", "text": ocr_item["text"], "confidence": ocr_item["confidence"], "quad": ocr_item["quad"]})
            obj_id += 1
        for gsam_item in gsam_data:
            obj = {"id": obj_id, "type": "object", "label": gsam_item["label"], "confidence": gsam_item["confidence"]}
            if "bbox" in gsam_item: obj["bbox"] = gsam_item["bbox"]
            if "svg_path" in gsam_item: obj["svg_path"] = gsam_item["svg_path"]
            if "layer" in gsam_item: obj["layer"] = gsam_item["layer"]
            metadata["objects"].append(obj)
            obj_id += 1
        metadata_json = json.dumps(metadata, ensure_ascii=False, separators=(",", ":"))
        user_prompt += f"METADATA:\n{metadata_json}\n\n"
        user_prompt += "Generate the complete SVG with precise metadata integration and appropriate hint strategy for recognizable subjects."
        return system_prompt, user_prompt

    def generate_svg(self, image_path: str) -> Optional[str]:
        image_id = extract_image_id(image_path)
        W, H = get_image_size(image_path)
        ocr_data = self.loader.load_ocr_data(image_id)
        gsam_data = self.loader.load_gsam_data(image_path, image_id)
        system_prompt, user_prompt = self.build_prompt(W, H, ocr_data, gsam_data)
        try:
            with open(image_path, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode('utf-8')
            mime_type = get_image_mime_type(image_path)
            response = self.client.chat.completions.create(
                model=self.args.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}, {"type": "text", "text": user_prompt}]}
                ],
                stream=False,
                max_tokens=self.args.max_tokens
            )
            raw_content = response.choices[0].message.content.strip()
            return clean_svg_output(raw_content)
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None

def batch_process_images(args):
    if not os.path.exists(args.images_folder):
        print(f"Error: Images folder {args.images_folder} not found")
        return
    image_files = get_image_files(args.images_folder)
    if not image_files:
        print(f"No images found in {args.images_folder}")
        return
    print(f"Found {len(image_files)} images")
    print(f"OCR metadata: {'✓' if args.ocr_metadata_txt and os.path.exists(args.ocr_metadata_txt) else '✗ Missing'}")
    print(f"GSAM metadata: {'✓' if args.gsam_metadata_folder and os.path.exists(args.gsam_metadata_folder) else '✗ Missing'}")
    print()
    generator = SVGGenerator(args)
    successful_count = 0
    failed_count = 0
    os.makedirs(args.svg_output_dir, exist_ok=True)
    for i, image_path in enumerate(image_files, 1):
        rel_path = os.path.relpath(image_path, args.images_folder)
        print(f"[{i}/{len(image_files)}] Processing: {rel_path}")
        svg_code = generator.generate_svg(image_path)
        if svg_code:
            svg_rel_dir = os.path.dirname(rel_path)
            svg_output_dir = os.path.join(args.svg_output_dir, svg_rel_dir) if svg_rel_dir else args.svg_output_dir
            os.makedirs(svg_output_dir, exist_ok=True)
            svg_filename = f"{Path(rel_path).stem}.svg"
            svg_path = os.path.join(svg_output_dir, svg_filename)
            try:
                with open(svg_path, 'w', encoding='utf-8') as f:
                    f.write(svg_code)
                tokens = count_tokens(svg_code)
                print(f"  ✓ Success - SVG saved: {svg_path} (tokens: {tokens})")
                successful_count += 1
            except Exception as e:
                print(f"  ✗ Error saving SVG: {e}")
                failed_count += 1
        else:
            failed_count += 1
            print(f"  ✗ Failed")
        if i < len(image_files):
            time.sleep(args.sleep_between_calls)
    print(f"\nProcessing completed: {successful_count} successful, {failed_count} failed")
    print(f"SVG files saved to: {args.svg_output_dir}")

def main():
    parser = argparse.ArgumentParser(
        description="img2svg Converter with Metadata Integration for Visual Question Answering.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('--images-folder', type=str, required=True, help='Path to the root folder containing images to process.')
    parser.add_argument('--svg-output-dir', type=str, default='./generated_svgs', help='Directory to save the generated SVG files.')
    parser.add_argument('--ocr-metadata-txt', type=str, default=None, help='Path to the OCR metadata file (e.g., system_results.txt).')
    parser.add_argument('--gsam-metadata-folder', type=str, default=None, help='Path to the folder containing GSAM metadata JSON files.')
    
    parser.add_argument('--base-url', type=str, default="https://tao.plus7.plus/v1", help='API base URL.')
    parser.add_argument('--api-key', type=str, default=os.getenv("OPENAI_API_KEY"), help='API key. Can also be set via OPENAI_API_KEY environment variable.')
    parser.add_argument('--model', type=str, default="claude-4-opus", help='Model name to use for generation.')
    parser.add_argument('--max-tokens', type=int, default=16384, help='Maximum number of tokens for the API response.')
    
    parser.add_argument('--sleep-between-calls', type=int, default=5, help='Seconds to sleep between API calls to avoid rate limiting.')
    parser.add_argument('--max-text-items', type=int, default=1000, help='Maximum number of OCR items to process per image.')
    parser.add_argument('--max-text-len', type=int, default=10000, help='Maximum length of a single OCR text item.')
    parser.add_argument('--simplify-polygons', action='store_true', help='Enable polygon simplification for GSAM data.')
    parser.add_argument('--no-simplify-polygons', action='store_false', dest='simplify_polygons', help='Disable polygon simplification.')
    parser.add_argument('--simplification-max-area-loss', type=float, default=0.003, help='Maximum allowed area loss percentage during polygon simplification.')
    
    parser.set_defaults(simplify_polygons=True)
    
    args = parser.parse_args()

    if not args.api_key:
        parser.error("API key is required. Provide it via --api-key or set the OPENAI_API_KEY environment variable.")
        
    print("=== img2svg Converter with Metadata Integration ===")
    print("Task: Convert images to SVG for Visual Question Answering")
    print("Features: OCR + GSAM metadata + Hint strategy for special cases")
    print()
    
    batch_process_images(args)
    
    print("\nProcessing complete!")

if __name__ == "__main__":
    main()