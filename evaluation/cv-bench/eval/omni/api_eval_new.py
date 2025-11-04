import argparse
import os
import json
import base64
import requests
import time
from tqdm import tqdm
from pathlib import Path

# from zai import ZhipuAiClient

zhipu_client = None

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# def gpt_answer(image_path, full_prompt, args):
#     """
#     调用 Zhipu AI API (GLM)，但保持输入输出接口与原 requests 版本完全一致。
#     """
#     global zhipu_client # 声明我们将使用全局客户端实例

#     # 1. [核心改动] 如果客户端未初始化，则使用 args.api_key 初始化一次
#     if zhipu_client is None:
#         print("首次调用，正在初始化 Zhipu AI 客户端...")
#         zhipu_client = ZhipuAiClient(api_key=args.api_key)

#     # 2. [保持一致] 图片编码和 FileNotFoundError 处理逻辑不变
#     try:
#         with open(image_path, "rb") as image_file:
#             base64_image = base64.b64encode(image_file.read()).decode('utf-8')
#     except FileNotFoundError:
#         print(f"\n错误: 找不到图像文件 {image_path}")
#         return "IMAGE_NOT_FOUND"
    
#     # 3. [保持一致] MIME 类型检测逻辑不变
#     file_extension = os.path.splitext(image_path)[1].lower()
#     mime_types = {
#         '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
#         '.gif': 'image/gif', '.webp': 'image/webp', '.bmp': 'image/bmp'
#     }
#     mime_type = mime_types.get(file_extension, 'application/octet-stream')

#     # 4. [核心改动] 构建 Zhipu AI SDK 需要的 messages 列表
#     messages_payload = [
#         {
#             "role": "user",
#             "content": [
#                 {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
#                 {"type": "text", "text": full_prompt}
#             ]
#         }
#     ]

#     # 5. [核心改动] 使用 Zhipu AI SDK 调用 API，并保持重试逻辑
#     try:
#         response = zhipu_client.chat.completions.create(
#             model=args.model_name,
#             messages=messages_payload,
#             temperature=0.0,
#             max_tokens=128,
#             thinking={"type": "disabled"} # 遵从您的指示
#         )
#         output = response.choices[0].message.content
#         time.sleep(2) # [保持一致] 保持原有的延时
#         return output
#     except Exception as e:
#         print(f"\nZhipu API 请求或解析失败: {e}, 等待10秒后重试...")
#         time.sleep(10) # [保持一致] 保持原有的延时
#         # [保持一致] 递归调用自身以实现重试，函数签名不变
#         return gpt_answer(image_path, full_prompt, args)


def gpt_answer(image_path, full_prompt, args):
    try:
        base64_image = encode_image(image_path)
    except FileNotFoundError:
        print(f"\nError: Cannot find image file {image_path}")
        return "IMAGE_NOT_FOUND"
    
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {args.api_key}"
    }
    endpoint_url = f"{args.base_url}/chat/completions"
    
    file_extension = os.path.splitext(image_path)[1].lower()
    mime_types = {
        '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.gif': 'image/gif', '.webp': 'image/webp', '.bmp': 'image/bmp'
    }
    mime_type = mime_types.get(file_extension, 'application/octet-stream')
    
    payload = {
        "model": args.model_name,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
                    {"type": "text", "text": full_prompt}
                ]
            }
        ],
        "temperature": args.temperature,
        "max_tokens": args.max_new_tokens
    }
      
    try:
        response = requests.post(endpoint_url, headers=headers, json=payload)
        response.raise_for_status()
        output = response.json()['choices'][0]['message']['content']
        time.sleep(1)
        return output
    except Exception as e:
        print(f"\nAPI Request failed: {e}, Waiting 10 seconds to retry...")
        time.sleep(10)
        return gpt_answer(image_path, full_prompt, args)


def eval_omni(args):
    all_questions = []
    for ann_file in Path(args.data_root).rglob("annotations.jsonl"):
        with open(ann_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    all_questions.append(json.loads(line))
        
    os.makedirs(os.path.dirname(args.answers_file), exist_ok=True)
    ans_file = open(args.answers_file, "w")

    omni_questions = [q for q in all_questions if q.get('source') == 'Omni3D']
    print(f"Found {len(omni_questions)} Omni3D sample to eval")

    for idx, line in enumerate(tqdm(omni_questions, desc=f"Eval Omni3D (Model: {args.model_name})")):

        img_path = os.path.join(args.data_root, line["image_path"])
        question = line["question"]
        choices = line.get("choices", [])
        labeled_choices = [f"({chr(65 + i)}) {choice}" for i, choice in enumerate(choices)]
        formatted_choices = "\n".join(labeled_choices)
        addition = f"\n{args.question_extension}"
        full_prompt = f"{question}\n{formatted_choices}{addition}"
        outputs = gpt_answer(img_path, full_prompt, args)

        ans_file.write(json.dumps({
            "questionId": idx,
            "image": line["image_path"],
            "prompt": full_prompt,
            "answer": outputs,
            "gt_answer": line["answer"],
            "source": line["source"],
            "category": line.get("task", ""),
            "options": line.get("choices", []),
            "model_id": args.model_name
        }) + "\n")
        ans_file.flush()

    ans_file.close()
    print(f"\nOmni3D Eval done! Result is saved: {args.answers_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Only Omni3D samples from CV-Bench are evaluated.")
    
    parser.add_argument("--data_root", type=str, required=True,
                        help="CV-Bench data root directory (eg. CV-Bench-100sample)")
    parser.add_argument("--answers_file", type=str, default="./gpt_eval_data/answers_omni.jsonl")
    parser.add_argument("--question_extension", type=str, default="Answer with the option's letter from the given choices directly.") # 保留 Omni 特有的指令
    parser.add_argument("--api_key", type=str, required=True, help="API key for Authentication")
    parser.add_argument("--base_url", type=str, default="https://tao.plus7.plus/v1", help="API Base URL")
    parser.add_argument("--model_name", type=str, default="gpt-4o", help="Model name")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max_new_tokens", type=int, default=16, help="Maximum number of new tokens to generate")
    
    args = parser.parse_args()
    eval_omni(args)
