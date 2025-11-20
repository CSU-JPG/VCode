# 🎨 VCode: SVG as Symbolic Visual Representation

<p align="center">
<a href="https://csu-jpg.github.io/VCode" target="_blank"><img src="https://img.shields.io/badge/Project-Page-brightgreen"></a>
<a href="https://github.com/CSU-JPG/VCode" target="_blank"><img src="https://img.shields.io/badge/Code-GitHub-black"></a>
<a href="https://arxiv.org/abs/2511.02778" target="_blank"><img src="https://img.shields.io/badge/arXiv-2511.02778-red"></a>
<a href="https://huggingface.co/spaces/CSU-JPG/VCode" target="_blank"><img src="https://img.shields.io/badge/🤗%20HuggingFace Space-VCode-ffd21e"></a>
<a href="https://huggingface.co/papers/2511.02778" target="_blank"><img src="https://img.shields.io/badge/🤗%20Daily%20Papers-2511.02778-ffd21e"></a>
</p>


**TL;DR:** SVG code as a Visual Representation



<img src="./assets/teaser.png" alt="Overview"/>

**See our demo video for fun!**

<p align="center">
  <video src="https://github.com/user-attachments/assets/2d202222-4934-4bc0-ae69-b231fc507d02"
         style="max-width: 80%; height: auto; border-radius: 10px;"
         controls
         muted>
  </video>
</p>

## 📣 News
- **[2025.11.08]** 🌟 Added Gemini-3-Pro to our benchmark, showing excellent performance.
- **[2025.11.08]** 🎥 Released our **demo video** featuring lots of fun memes and reaction images converted into SVGs.
- **[2025.11.08]** 🚀 We now offer a **free trial API** on our 🤗 **[HuggingFace Space](https://huggingface.co/spaces/CSU-JPG/VCode)**.
- **[2025.11.05]** 🔥 We are honored to be featured as 🤗 **[HuggingFace Daily Paper #1](https://huggingface.co/papers/2511.02778)**.

## 📋 Table of Contents

<!--- [📚 Introduction](#-introduction)-->

- [🛠️ Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
- [🔮 Evaluation](#-evaluation)
- [📌 Citation](#-citation)
---

## 🛠️ Installation

**Environment**

```bash
git clone -b main --single-branch https://github.com/CSU-JPG/VCode.git
cd VCode
conda create -n vcode python=3.10.2 -y
conda activate vcode
conda install pytorch=2.5.1 torchvision=0.20.1 torchaudio=2.5.1 pytorch-cuda=12.4 -c pytorch -c nvidia
pip install -r requirements.txt
```

---

## 🚀 Quick Start

### 🧩 VCode-suite

**VCode-suite** is a comprehensive toolkit that automates the full image-to-SVG-to-render workflow.
It includes both integrated pipelines and independent modules for generation, rendering, and revision.
Users can either run the end-to-end pipelines for batch processing, or execute individual scripts for customized control.

```
📁 vcode-suite/
├── filter.py
├── img2svg.py
├── img2svgthinking.py
├── img2svg-w-visual-tool.py
├── img2text2svg.py
├── pipeline.sh
├── revision_pipeline.sh
├── revision.py
└── svg_render_img.py
```

> 💡 **Tip:**
> The **pipelines (`pipeline.sh`, `revision_pipeline.sh`)** perform fully automated batch processing,
> while the **Python scripts** (`img2svg.py`, `img2text2svg.py`, `revision.py`, etc.) can be run independently
> to support flexible and modular experimentation within the VCode framework.


### ⚙️ Usage

#### 1️⃣ Generate and render SVGs

`pipeline.sh` orchestrates the full image-to-SVG-to-render workflow.
It can connect to different generation modules — `img2svg`, `img2text2svg`, or `img2svgthinking` — to convert images into SVGs, then filter and render them into pixel images.

```bash
chmod +x pipeline.sh
./pipeline.sh
```

#### 2️⃣ Optimize generated SVGs

`revision_pipeline.sh` automates the revision and optimization process.
It takes the previously generated SVGs (`generated_svgs/`) and rendered images (`generated_imgs/`), calls the API-based revision module, and outputs the optimized SVGs and renders to `optimized_svgs/` and `optimized_imgs/`.

```bash
chmod +x revision_pipeline.sh
./revision_pipeline.sh
```

#### 3️⃣ Run scripts independently

Both generation and revision scripts can be executed independently for flexible and customized workflows.

Each core generation script — `img2svg.py`, `img2text2svg.py`, `img2svgthinking.py`, and `img2svg-w-visual-tool.py` — can directly convert input images into SVG code.
Similarly, `revision.py` can be run independently to optimize previously generated SVGs through visual feedback.

---

**Run `img2svg.py`**

```bash
python vcode-suite/img2svg.py \
/path/to/input_images \
./generated_svgs \
--model gpt-5 \
--base-url https://openrouter.ai/api/v1 \
--api-key <OPENROUTER_API_KEY> \
--max-tokens 16384
```

| Argument            | Type | Default                        | Description                                               |
| ------------------- | ---- | ------------------------------ | --------------------------------------------------------- |
| `images_folder`     | str  | -                              | Path to the input folder containing image files.          |
| `svg_output_folder` | str  | -                              | Directory to save the generated SVG files.                |
| `--model`           | str  | `gpt-5`                        | API model name used for conversion.                       |
| `--base-url`        | str  | `https://openrouter.ai/api/v1` | Base URL of the API endpoint.                             |
| `--api-key`         | str  | -                              | API key for authentication.                               |
| `--sleep`           | int  | `5`                            | Seconds to wait between consecutive API calls.            |
| `--max-tokens`      | int  | `16384`                        | Maximum number of tokens allowed in the model’s response. |

---

**Run `revision.py`**

```bash
python vcode-suite/revision.py \
--svg-folder ./generated_svgs \
--original-folder ./input_images \
--rendered-folder ./generated_imgs \
--output-folder ./optimized_svgs \
--analysis-folder ./visual_analysis \
--base-url https://openrouter.ai/api/v1 \
--api-key <OPENROUTER_API_KEY> \
--model gpt-5 \
--max-tokens 16384
```

| Argument            | Type | Default                        | Description                                             |
| ------------------- | ---- | ------------------------------ | ------------------------------------------------------- |
| `--svg-folder`      | str  | —                              | Root directory containing the SVG files to optimize.    |
| `--svg-folder`      | str  | -                              | Root directory containing the SVG files to optimize.    |
| `--original-folder` | str  | -                              | Directory of the original reference images.             |
| `--rendered-folder` | str  | -                              | Directory of rendered images corresponding to the SVGs. |
| `--output-folder`   | str  | -                              | Directory to save the optimized SVG files.              |
| `--analysis-folder` | str  | -                              | Directory to save visual comparison and analysis txts.  |
| `--base-url`        | str  | `https://openrouter.ai/api/v1` | Base URL of the API endpoint.                           |
| `--api-key`         | str  | -                              | API key.                                                |
| `--model`           | str  | `gpt-5`                        | Model used for revision.                                |
| `--max-tokens`      | int  | `16384`                        | Maximum tokens allowed in the model response.           |

> 💡 **Tip:**
> The `revision.py` script refines existing SVGs based on visual comparison feedback, while generation scripts (`img2svg.py`, `img2text2svg.py`, `img2svgthinking.py`, `img2svg-w-visual-tool.py`) create SVGs from input images_folder.
> You can flexibly mix and match these tools depending on your pipeline needs.

---

## 🔮 Evaluation

### ⚙️ Usage

#### 1️⃣ Generate IMGs for all three datasets

Use the VCode-suite pipeline (or standalone scripts) to render images for each dataset.
Original images are already in `data/`:

- **MM-Vet:** `data/mm-vet/images`
- **CV-Bench:** `data/cv-bench`
- **MMMU:** `data/mmmu/mmmu_dev_processed_single_img_subset`

Running your pipeline will produce, per dataset, a folder like:

```
generated_svgs/
generated_imgs/  ← used by the evaluators
```

---

#### 2️⃣ Run each dataset’s evaluator

Each evaluator is a shell script under `evaluation/…`. They all follow the same usage:

```bash
chmod +x evaluation/mm-vet/mmvet_eval.sh
./evaluation/mm-vet/mmvet_eval.sh
```

```bash
chmod +x evaluation/cv-bench/cvbench_eval.sh
./evaluation/cv-bench/cvbench_eval.sh
```

```bash
chmod +x evaluation/mmmu/mmmu_eval.sh
./evaluation/mmmu/mmmu_eval.sh
```

These scripts will read your `generated_imgs/` and compute scores.

> 💡 **Reference:** For directory organization and example script configuration, see **`example_results/`** (it shows a working layout you can mirror).


---

#### 3️⃣ Calculate each dataset’s metrics


**Full Command with Options**

```bash
python metrics.py \
--folder1 /path/to/reference_images \
--folder2 /path/to/model_outputs/gpt-4o \
--ckpt google/siglip2-so400m-patch14-384
```

**Command Line Arguments**

| Argument    | Required | Default                             | Description                                                                      |
| ----------- | -------- | ----------------------------------- | -------------------------------------------------------------------------------- |
| `--folder1` | ✅ Yes    | -                                   | Path to reference images folder                                                  |
| `--folder2` | ✅ Yes    | -                                   | Path to model output folder (containing `generated_imgs/` and `generated_svgs/`) |
| `--ckpt`    | ❌ No     | `google/siglip2-so400m-patch14-384` | SigLIP model checkpoint                                                          |


**Expected Directory Layout:**

**Reference Images Folder** (`--folder1`)

**Location:** `data/mm-vet/images` *(example path - can be customized)*
```
folder1/
├── category1/
│   ├── image001.png
│   ├── image002.jpg
│   └── ...
├── category2/
│   ├── image003.png
│   └── ...
└── ...
```

**Model Output Folder** (`--folder2`)

**Location:** `example_results/mm-vet/Gemini-2.5-Pro` *(example path - can be customized)*
```
folder2/
├── generated_imgs/           # Generated/rendered images
│   ├── category1/
│   │   ├── image001.png
│   │   ├── image002.jpg
│   │   └── ...
│   ├── category2/
│   │   ├── image003.png
│   │   └── ...
│   └── ...
│
└── generated_svgs/           # SVG source files
   ├── category1/
   │   ├── image001.svg
   │   ├── image002.svg
   │   └── ...
   ├── category2/
   │   ├── image003.svg
   │   └── ...
   └── ...
```


---

## 📌 Citation
If you find our work useful, please cite:

```bibtex
@misc{vcode,
      title={VCode: a Multimodal Coding Benchmark with SVG as Symbolic Visual Representation}, 
      author={Kevin Qinghong Lin and Yuhao Zheng and Hangyu Ran and Dantong Zhu and Dongxing Mao and Linjie Li and Philip Torr and Alex Jinpeng Wang},
      year={2025},
      eprint={2511.02778},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2511.02778}, 
}
```

