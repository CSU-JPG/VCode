#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
import shutil

def copy_annotations(src_root: Path, dist_root: Path):

    for ann_file in src_root.rglob("annotations.jsonl"):
        rel_path = ann_file.relative_to(src_root)
        dst_file = dist_root / rel_path

        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ann_file, dst_file)
        print(f"✔ Copied {ann_file} -> {dst_file}")

def main():
    ap = argparse.ArgumentParser(description="Copy annotations.jsonl files from source to destination")
    ap.add_argument("--src_root", required=True, help="Source root directory containing annotations.jsonl files")
    ap.add_argument("--base_dir", required=True, help="Base directory where generated_imgs will be created")
    args = ap.parse_args()

    src_root = Path(args.src_root).resolve()
    dist_root = Path(args.base_dir).resolve() / "generated_imgs"

    if not src_root.exists():
        raise FileNotFoundError(f"Source root directory doesn't exist: {src_root}")
    if not dist_root.exists():
        raise FileNotFoundError(f"Dist root directory doesn't exit: {dist_root}")

    copy_annotations(src_root, dist_root)

if __name__ == "__main__":
    main()
