"""
siglip_score_and_token_stats.py

Compute SigLIP similarity between reference images and generated images,
calculate success rate, and analyze token usage of generated SVG files.

- Folder 1: reference or dataset images
- Folder 2: model folder (e.g., gpt-5) containing:
  - generated_imgs/: rendered images for similarity comparison
  - generated_svgs/: SVG files for token counting
"""
import argparse
from pathlib import Path
from tqdm import tqdm
import torch
import torch.nn.functional as F
from transformers import SiglipProcessor, SiglipModel
from transformers.image_utils import load_image
import tiktoken


# ==========================================================
# =============== SigLIP Similarity Section ================
# ==========================================================

def load_siglip_model(ckpt: str = "google/siglip2-so400m-patch14-384"):
    """Load SigLIP model and processor."""
    model = SiglipModel.from_pretrained(ckpt, device_map="auto").eval()
    processor = SiglipProcessor.from_pretrained(ckpt)
    return model, processor


def compute_image_similarity_siglip(model, processor, image_path1: str, image_path2: str) -> float:
    """Compute cosine similarity between two images using SigLIP embeddings."""
    image1, image2 = load_image(image_path1), load_image(image_path2)
    inputs1 = processor(images=[image1], return_tensors="pt").to(model.device)
    inputs2 = processor(images=[image2], return_tensors="pt").to(model.device)
    with torch.no_grad():
        emb1 = F.normalize(model.get_image_features(**inputs1), p=2, dim=-1)
        emb2 = F.normalize(model.get_image_features(**inputs2), p=2, dim=-1)
    return F.cosine_similarity(emb1, emb2, dim=-1).item()


def get_image_files(folder_path: str, extensions=('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')) -> list[str]:
    """Recursively collect all image files under a directory."""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Folder not found: {folder_path}")
        return []
    files = []
    for ext in extensions:
        files.extend(folder.rglob(f"*{ext}"))
        files.extend(folder.rglob(f"*{ext.upper()}"))
    return sorted(map(str, files))


def match_images_by_relative_path(folder1_files, folder2_files, folder1_root, folder2_root):
    """Match two image sets by identical relative paths (excluding extensions)."""
    def rel_key(file_path, root):
        rel = str(Path(file_path).relative_to(root)).replace("\\", "/")
        return str(Path(rel).with_suffix(""))

    map1 = {rel_key(f, folder1_root): f for f in folder1_files}
    map2 = {rel_key(f, folder2_root): f for f in folder2_files}
    common_keys = sorted(set(map1.keys()) & set(map2.keys()))
    return [(map1[k], map2[k]) for k in common_keys]


def batch_compare_folders_siglip(folder1_path: str, generated_imgs_path: str, ckpt: str):
    """Batch compute SigLIP cosine similarity between reference and generated images."""
    print("=" * 70)
    print("🧩 SigLIP Batch Image Similarity Evaluation")
    print("=" * 70)

    model, processor = load_siglip_model(ckpt)

    print(f"Scanning reference folder: {folder1_path}")
    folder1_files = get_image_files(folder1_path)
    reference_count = len(folder1_files)
    print(f"Found {reference_count} reference images.")

    print(f"Scanning generated images folder: {generated_imgs_path}")
    folder2_files = get_image_files(generated_imgs_path)
    generated_count = len(folder2_files)
    print(f"Found {generated_count} generated images.")

    if reference_count == 0:
        print("No reference images found.")
        return 0.0, 0.0

    # Calculate success rate
    success_rate = generated_count / reference_count if reference_count > 0 else 0.0
    print(f"\n📊 Success Rate: {generated_count}/{reference_count} = {success_rate:.4f} ({success_rate*100:.2f}%)")

    if generated_count == 0:
        print("No generated images found.")
        return 0.0, success_rate

    matched_pairs = match_images_by_relative_path(folder1_files, folder2_files, folder1_path, generated_imgs_path)
    matched_count = len(matched_pairs)
    unmatched_count = generated_count - matched_count

    print(f"\nMatched pairs: {matched_count}")
    print(f"Unmatched images: {unmatched_count}")

    similarities = []
    print("\nComputing SigLIP similarities...")
    for img1, img2 in tqdm(matched_pairs, desc="Progress"):
        try:
            sim = compute_image_similarity_siglip(model, processor, img1, img2)
            similarities.append(sim)
        except Exception as e:
            print(f"Error processing {Path(img1).name}: {e}")
            similarities.append(0.0)

    # Only penalize unmatched images in generated folder
    similarities.extend([0.0] * unmatched_count)
    avg_sim = sum(similarities) / len(similarities) if similarities else 0.0

    print(f"\n✅ Average SigLIP cosine similarity: {avg_sim:.6f}")
    print("=" * 70)
    return avg_sim, success_rate


# ==========================================================
# =============== SVG Token Counting Section ===============
# ==========================================================

def count_tokens(text: str) -> int:
    """Count token length using tiktoken."""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        return 0


def analyze_svg_tokens(folder_path: str):
    """
    Recursively count tokens of all SVG files under the given folder.
    """
    print("\n🧾 SVG Token Analysis")
    print("=" * 70)
    svg_files = list(Path(folder_path).rglob("*.svg"))
    print(f"Found {len(svg_files)} SVG files under {folder_path}.")

    if not svg_files:
        print("No SVG files found.")
        return 0, 0

    token_counts = []
    for i, file_path in enumerate(svg_files):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                token_counts.append(count_tokens(content))
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    total_tokens = sum(token_counts)
    avg_tokens = total_tokens / len(token_counts) if token_counts else 0

    print(f"✅ Processed {len(token_counts)} SVG files.")
    print(f"🔢 Total tokens: {total_tokens:,}")
    print(f"📈 Average tokens per SVG: {avg_tokens:.2f}")
    print("=" * 70)
    return total_tokens, avg_tokens


# ==========================================================
# ======================== Main ============================
# ==========================================================
def main():
    parser = argparse.ArgumentParser(
        description="Compute SigLIP similarity, success rate, and SVG token statistics."
    )
    parser.add_argument("--folder1", required=True, help="Path to the reference image folder.")
    parser.add_argument("--folder2", required=True, help="Path to the model folder (containing generated_imgs and generated_svgs).")
    parser.add_argument("--ckpt", default="google/siglip2-so400m-patch14-384",
                        help="SigLIP model checkpoint name.")
    args = parser.parse_args()

    # Construct paths for generated_imgs and generated_svgs
    model_folder = Path(args.folder2)
    generated_imgs_path = model_folder / "generated_imgs"
    generated_svgs_path = model_folder / "generated_svgs"

    # Validate paths
    if not model_folder.exists():
        print(f"❌ Error: Model folder does not exist: {args.folder2}")
        return

    if not generated_imgs_path.exists():
        print(f"⚠️  Warning: generated_imgs folder not found: {generated_imgs_path}")
        print("Creating empty folder...")
        generated_imgs_path.mkdir(parents=True, exist_ok=True)

    if not generated_svgs_path.exists():
        print(f"⚠️  Warning: generated_svgs folder not found: {generated_svgs_path}")
        print("Creating empty folder...")
        generated_svgs_path.mkdir(parents=True, exist_ok=True)

    print(f"\n📁 Model Folder: {args.folder2}")
    print(f"📁 Reference Images: {args.folder1}")
    print(f"📁 Generated Images: {generated_imgs_path}")
    print(f"📁 Generated SVGs: {generated_svgs_path}\n")

    # Compute similarity and success rate
    avg_similarity, success_rate = batch_compare_folders_siglip(
        args.folder1, str(generated_imgs_path), args.ckpt
    )

    # Analyze SVG tokens
    total_tokens, avg_tokens = analyze_svg_tokens(str(generated_svgs_path))

    # Final summary
    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    print(f"Success Rate: {success_rate:.4f} ({success_rate*100:.2f}%)")
    print(f"SigLIP Average Similarity: {avg_similarity:.6f}")
    print(f"Total SVG Tokens: {total_tokens:,}")
    print(f"Average SVG Tokens per File: {avg_tokens:.2f}")
    print("=" * 70)


if __name__ == "__main__":
    main()