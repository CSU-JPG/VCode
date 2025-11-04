from pathlib import Path
import sys
import cairosvg
from PIL import Image
import io
import argparse

def render_svgs_to_images(svg_input_dir, image_output_dir, reference_dir):
    """
    Converts SVG files to raster images (PNG or JPG), maintaining the directory structure
    and matching the file format of images in the reference directory.
    """
    input_path = Path(svg_input_dir)
    output_path = Path(image_output_dir)
    ref_path = Path(reference_dir)
    
    if not input_path.exists():
        print(f"❌ Error: Input SVG directory not found: {input_path}")
        return
    
    if not ref_path.exists():
        print(f"❌ Error: Reference directory not found: {ref_path}")
        return

    svg_files = sorted(list(input_path.rglob("*.svg")))
    
    if not svg_files:
        print(f"⚠️ No SVG files found in '{input_path}'.")
        return

    print(f"🔍 Found {len(svg_files)} SVG files. Starting conversion...")
    output_path.mkdir(parents=True, exist_ok=True)

    for i, svg_file in enumerate(svg_files, 1):

        relative_path = svg_file.relative_to(input_path)
        output_dir = output_path / relative_path.parent
        
        output_dir.mkdir(parents=True, exist_ok=True)
        name = svg_file.stem

        out_ext = ".png"
        if (ref_path / relative_path.with_suffix('.jpg')).exists() or \
           (ref_path / relative_path.with_suffix('.jpeg')).exists():
            out_ext = ".jpg"
        
        output_file = output_dir / f"{name}{out_ext}"

        try:
            # Render SVG to high-resolution PNG bytes in memory (3x scale)
            png_bytes = cairosvg.svg2png(url=str(svg_file), scale=3.0)

            if out_ext == ".png":
                with open(output_file, "wb") as f:
                    f.write(png_bytes)
            else:
                image = Image.open(io.BytesIO(png_bytes)).convert("RGB")
                image.save(output_file, "JPEG", quality=95, optimize=True)

            print(f"[{i}/{len(svg_files)}] ✅ {relative_path} → {output_file.relative_to('.')}")
        except Exception as e:
            error_msg = str(e).lower()
            if "no element found" in error_msg or "premature end of file" in error_msg:
                try:
                    svg_file.unlink()
                    print(f"[{i}/{len(svg_files)}] 🗑️ {relative_path}: Empty or invalid file detected, deleted.")
                except Exception as delete_error:
                    print(f"[{i}/{len(svg_files)}] ❌ {relative_path}: Failed to delete invalid file - {delete_error}")
            else:
                print(f"[{i}/{len(svg_files)}] ❌ {relative_path}: Conversion failed - {e}")

    print("✅ Conversion complete!")

def main():
    """Parses command-line arguments and starts the rendering process."""
    parser = argparse.ArgumentParser(
        description="Converts a directory of SVG files to high-resolution raster images (PNG or JPG)."
    )
    
    parser.add_argument(
        "--svg-input-dir",
        required=True,
        help="The source directory containing SVG files to be converted."
    )
    parser.add_argument(
        "--image-output-dir",
        required=True,
        help="The destination directory where rendered images will be saved."
    )
    parser.add_argument(
        "--reference-dir",
        required=True,
        help="Path to the directory of original images, used to match the output format (e.g., .jpg or .png)."
    )
    
    args = parser.parse_args()
    
    render_svgs_to_images(
        args.svg_input_dir, 
        args.image_output_dir, 
        args.reference_dir
    )

if __name__ == "__main__":
    main()