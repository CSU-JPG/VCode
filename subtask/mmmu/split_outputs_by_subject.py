import json
from pathlib import Path
from collections import defaultdict

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_json", type=Path, required=True,
                    help="Path to Unknown/output.json")
    ap.add_argument("--output_root", type=Path, required=True,
                    help="Root dir to save split subject folders")
    args = ap.parse_args()

    with args.input_json.open("r", encoding="utf-8") as f:
        records = json.load(f)

    by_subject = defaultdict(list)
    for rec in records:
        rec_id = rec["id"]
        try:
            # dev_<SubjectName>_<Number>
            subject = "_".join(rec_id.split("_")[1:-1])
        except Exception:
            subject = "Unknown"
        by_subject[subject].append(rec)

    for subj, items in by_subject.items():
        subj_dir = args.output_root / subj  
        subj_dir.mkdir(parents=True, exist_ok=True)
        out_path = subj_dir / "output.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"✅ {subj}: {len(items)} samples -> {out_path}")


if __name__ == "__main__":
    main()
