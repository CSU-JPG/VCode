import argparse
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(
        description="Copy subject-wise output.json files into target root directories (with local images)."
    )
    parser.add_argument(
        "--src_json_root", type=str, required=True,
        help="Source root dir where each subject has output.json (Parse&Eval format, empty responses)."
    )
    parser.add_argument(
        "--dst_root", type=str, required=True,
        help="Target root dir where each subject has images, but no output.json yet."
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="If set, will overwrite existing output.json in dst_root (default: skip)."
    )
    args = parser.parse_args()

    src_root = Path(args.src_json_root)
    dst_root = Path(args.dst_root)

    if not src_root.exists():
        raise FileNotFoundError(f"Source root {src_root} not found")
    if not dst_root.exists():
        raise FileNotFoundError(f"Destination root {dst_root} not found")

    for subj_dir in src_root.iterdir():
        if subj_dir.is_dir():
            src_json = subj_dir / "output.json"
            if not src_json.exists():
                print(f"⚠️  Skipping {subj_dir.name}, no output.json found.")
                continue

            dst_subj_dir = dst_root / subj_dir.name
            dst_subj_dir.mkdir(parents=True, exist_ok=True)
            dst_json = dst_subj_dir / "output.json"

            if dst_json.exists() and not args.overwrite:
                print(f"⏩ Skipping {subj_dir.name}, output.json already exists.")
                continue

            shutil.copy2(src_json, dst_json)
            print(f"✅ Copied {src_json} -> {dst_json}")


if __name__ == "__main__":
    main()
