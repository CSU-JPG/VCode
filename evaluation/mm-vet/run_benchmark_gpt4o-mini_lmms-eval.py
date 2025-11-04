import os
import json
import argparse
import base64
import requests
import traceback
import time
from tqdm import tqdm
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

def parse_args():
    parser = argparse.ArgumentParser(description="Inference on the MM-Vet Benchmark using the GPT-4o-mini API")
    parser.add_argument("--mmvet_path", type=str, required=True, help="MM-Vet dataset root directory")
    parser.add_argument("--mmvet_metadata", type=str, default="./mm-vet.json", help="MM-Vet metadata file path")
    parser.add_argument("--output_dir", type=str, default="mmvet_results-gpt4o-mini", help="Inference output directory")
    parser.add_argument("--model_name_tag", type=str, default="gpt-4o-mini", help="Final result JSON filename prefix")
    parser.add_argument("--api_key", type=str, required=True, help="OpenAI API Key")
    parser.add_argument("--system_prompt", type=str, default="You are a helpful assistant.", help="Optional system prompt")
    parser.add_argument("--max_tokens", type=int, default=1024, help="Max token")
    parser.add_argument("--max_retries", type=int, default=5, help="Maximum number of retries on failure")
    parser.add_argument("--model_name", type=str, default="gpt-4o-mini-2024-07-18", help="Model name")
    parser.add_argument("--base_url", type=str, default="https://api.openai.com/v1", help="API Base URL")
    return parser.parse_args()

def load_mmvet_data(mmvet_root_path,mmvet_metadata):
    print("📥 Loading MM-Vet metadata ...")
    meta_file = mmvet_metadata
    img_folder = os.path.join(mmvet_root_path, "generated_imgs")
    if not (os.path.exists(meta_file) and os.path.exists(img_folder)):
        raise FileNotFoundError("mm-vet.json or generated_imgs directory was not found.")

    with open(meta_file, "r") as f:
        data = json.load(f)

    sorted_ids = sorted(data.keys(), key=lambda x: int(x.split("_")[1]))
    data_list = []
    for idx, item_id in enumerate(sorted_ids):
        item = data[item_id]
        if not (item.get("imagename") and item.get("question")):
            continue
        img_path = os.path.join(img_folder, item["imagename"])
        data_list.append({
            "global_idx": idx,
            "id": item_id,
            "image_path": img_path,
            "question": item["question"]
        })
    print(f"✅ Successfully load {len(data_list)} samples ")
    return data_list

def encode_image_base64(image_path):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    if image_path.lower().endswith(".png"):
        return f"data:image/png;base64,{b64}"
    return f"data:image/jpeg;base64,{b64}"

def query_openai_api(base_url, image_b64_url, question, api_key, model_name, system_prompt=None, max_tokens=300, max_retries=5):
    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": question},
            {"type": "image_url", "image_url": {"url": image_b64_url}}
        ]
    })
    
    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "top_p": 1.0,
    }

    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                print(f"Non-200 response code: {response.status_code}, content: {response.text}")
                time.sleep(2 ** retries)
                retries += 1
                continue

            res_json = response.json()
            if "choices" in res_json:
                return res_json["choices"][0]["message"]["content"].strip()
            else:
                print("⚠️ No choices field found, please try again...")
        except Exception as e:
            print(f"Request exception: {e}")
            
        time.sleep(2 ** retries)
        retries += 1

    raise RuntimeError("Too many requests failed")

def main():
    args = parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    all_items = load_mmvet_data(args.mmvet_path,args.mmvet_metadata)

    results = []
    missing_image_ids = []
    temp_path = os.path.join(args.output_dir, "temp_results_cpu_0.json")
    finished_ids = set()

    if os.path.exists(temp_path):
        with open(temp_path, "r", encoding="utf-8") as f:
            prev = json.load(f)
            results.extend(prev)
            finished_ids = {item["id"] for item in prev if item["status"] in ["success", "error", "missing_image"]}
        print(f"🔁 Resume running from breakpoint: {len(finished_ids)} records have been completed; skip processing.")

    for idx, sample in enumerate(tqdm(all_items)):
        if sample["id"] in finished_ids:
            continue

        entry = {
            "global_idx": sample["global_idx"],
            "id": sample["id"],
            "generated_answer": None,
            "status": "pending",
            "error": None,
        }

        try:
            img_path = sample["image_path"]
            if not os.path.isfile(img_path):
                raise FileNotFoundError(f"Cannot find image file: {img_path}")

            image_b64_url = encode_image_base64(img_path)

            pre_prompt = "First please perform reasoning, and think step by step to provide best answer to the following question: \n\n"
            formatted_question = pre_prompt + sample["question"]

            answer = query_openai_api(
                args.base_url,
                image_b64_url,
                formatted_question,
                args.api_key,
                args.model_name,
                system_prompt=args.system_prompt,
                max_tokens=args.max_tokens,
                max_retries=args.max_retries,
            )
            entry.update({"generated_answer": answer, "status": "success"})

        except FileNotFoundError as e:
            entry.update({"status": "missing_image", "error": str(e)})
            missing_image_ids.append(sample["id"])

        except Exception as e:
            entry.update({
                "status": "error",
                "error": f"{str(e).splitlines()[0]}\n{traceback.format_exc()}"
            })

        results.append(entry)

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

    final_answers = {}
    missing_total = []

    for item in results:
        if item["status"] == "success":
            final_answers[item["id"]] = item["generated_answer"]
        elif item["status"] == "missing_image":
            missing_total.append(item["id"])
        else:
            final_answers[item["id"]] = "Processing failed - Error:" + item.get("error", "Unknown error").splitlines()[0]

    final_path = os.path.join(args.output_dir, f"{args.model_name_tag}.json")
    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(final_answers, f, indent=4, ensure_ascii=False)

    if missing_total:
        miss_path = os.path.join(args.output_dir, "missing_image_questions.json")
        with open(miss_path, "w", encoding="utf-8") as f:
            json.dump(sorted(set(missing_total)), f, indent=4, ensure_ascii=False)
        print(f"⚠️  A total of {len(missing_total)} problems are missing images, which have been recorded in {miss_path}.")

    print(f"🎉 Inference complete! Write to {final_path}")

if __name__ == "__main__":
    main()

