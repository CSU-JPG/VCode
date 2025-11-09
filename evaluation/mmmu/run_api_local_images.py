import os, random, base64, json
import numpy as np
from tqdm import tqdm
from argparse import ArgumentParser
from pathlib import Path
from PIL import Image

from datasets import load_dataset
from utils.data_utils import load_yaml, construct_prompt, process_single_sample
from utils.eval_utils import parse_multi_choice_response
from openai import OpenAI
from zai import ZhipuAiClient

def encode_image(pil_image):
    import io
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def call_api_engine(args, sample):
    client = OpenAI(
        base_url=args.base_url,
        api_key=args.api_key
    )

    content = [{"type": "text", "text": sample["prompt"]}]
    if "image" in sample and sample["image"] is not None:
        base64_img = encode_image(sample["image"])
        content.insert(0, {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_img}"}
        })

    resp = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": content}],
        temperature=args.config.get("temperature", 0),
        max_tokens=4096,
        stream=False
    )
    return resp.choices[0].message.content.strip()


# def call_api_engine(args, sample):
#     client = ZhipuAiClient(
#         api_key=args.api_key
#     )

#     content = [{"type": "text", "text": sample["prompt"]}]
#     if "image" in sample and sample["image"] is not None:
#         base64_img = encode_image(sample["image"])
#         content.insert(0, {
#             "type": "image_url",
#             "image_url": {"url": f"data:image/png;base64,{base64_img}"}
#         })

#     resp = client.chat.completions.create(
#         model=args.model,
#         messages=[{"role": "user", "content": content}],
#         temperature=args.config.get("temperature", 0),
#         max_tokens=4096,
#         # stream=False,  
#         thinking={"type": "disabled"}
#     )
    
#     return resp.choices[0].message.content.strip()


def run_model(args, samples, call_model_engine_fn):
    out_samples = {}
    for sample in tqdm(samples):
        if sample.get("image") is None:
            print(f"⚠️ Image not found for {sample['id']}")
            out_samples[sample["id"]] = "IMAGE_NOT_FOUND"
            continue

        response = call_model_engine_fn(args, sample)
        if sample["question_type"] == "multiple-choice":
            pred_ans = parse_multi_choice_response(
                response, sample["all_choices"], sample["index2ans"]
            )
        else:
            pred_ans = response
        out_samples[sample["id"]] = pred_ans
    return out_samples


def save_outputs(args, samples, preds):
    records = []
    for sample in samples:
        rec = {
            "id": sample["id"],
            "question_type": sample["question_type"],
            "answer": sample.get("answer", ""),
            "all_choices": sample.get("all_choices", []),
            "index2ans": sample.get("index2ans", {}),
            "response": preds.get(sample["id"], "")
        }
        records.append(rec)

    out_root = Path(args.output_path) / "Unknown"
    out_root.mkdir(parents=True, exist_ok=True)
    out_path = out_root / "output.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(records)} samples -> {out_path}")


# ===== main =====
def main():
    parser = ArgumentParser()
    parser.add_argument("--output_path", type=str, required=True,
                        help="Root dir to save outputs (will save in Unknown/output.json)")
    parser.add_argument("--data_path", type=str, required=True,
                        help="Root dir with subject subfolders that contain images and output.json for id list")
    parser.add_argument("--api_key", type=str, required=True, help="API key string")
    parser.add_argument("--model", type=str, required=True, help="Model name, e.g. claude-4-opus")
    parser.add_argument('--config_path', type=str, default="configs/api.yaml")
    parser.add_argument("--cache_dir", type=str, default=None,
                        help="Path to HuggingFace cache dir (for text metadata only)")
    parser.add_argument("--base_url", type=str, default="https://tao.plus7.plus/v1",
                        help="Base URL for API endpoint")
    args = parser.parse_args()

    args.config = load_yaml(args.config_path)
    for key, value in args.config.items():
        if key != "eval_params" and isinstance(value, list):
            assert len(value) == 1
            args.config[key] = value[0]

    id_set = set()
    root = Path(args.data_path)
    for subj_dir in root.iterdir():
        if subj_dir.is_dir():
            out_path = subj_dir / "output.json"
            if not out_path.exists():
                continue
            with out_path.open("r", encoding="utf-8") as f:
                local_records = json.load(f)
                ids = [rec["id"] for rec in local_records if "id" in rec]
                id_set.update(ids)

    dataset = []
    for subject in os.listdir(root):
        subj_dir = root / subject
        if not subj_dir.is_dir():
            continue
        if subject.startswith("."):
            continue
        print(f"📥 Loading HF dataset for {subject}")
        try:
            hf_dataset = load_dataset("MMMU/MMMU", subject, split="dev", cache_dir=args.cache_dir)
        except Exception as e:
            print(f"⚠️ Failed to load HF dataset for {subject}: {e}")
            continue

        if "image" in hf_dataset.column_names:
            hf_dataset = hf_dataset.remove_columns(["image"])

        for rec in hf_dataset:
            _id = rec.get("id")
            if _id in id_set:
                rec = dict(rec)
                dataset.append(rec)

    samples = []
    for sample in dataset:
        if isinstance(sample.get("options"), list):
            sample["options"] = str(sample["options"])

        sample = process_single_sample(sample)
        sample = construct_prompt(sample, args.config)

        if "final_input_prompt" in sample:
            sample["prompt"] = sample["final_input_prompt"]
        elif "prompt" in sample:
            sample["prompt"] = sample["prompt"]
        elif "empty_prompt" in sample:
            sample["prompt"] = sample["empty_prompt"]
        else:
            print(f"⚠️ construct_prompt failed for {sample.get('id')}, set empty prompt.")
            sample["prompt"] = ""

        _id = sample["id"]
        img_path = None
        for subj_dir in root.iterdir():
            candidate = subj_dir / f"{_id}_img1.png"
            if candidate.exists():
                img_path = candidate
                break

        if img_path and img_path.exists():
            try:
                sample["image"] = Image.open(img_path).convert("RGB")
            except Exception as e:
                print(f"⚠️ Failed to open image {img_path}: {e}")
                sample["image"] = None
        else:
            sample["image"] = None

        samples.append(sample)

    out_samples = run_model(args, samples, call_api_engine)
    save_outputs(args, samples, out_samples)


if __name__ == "__main__":
    main()
