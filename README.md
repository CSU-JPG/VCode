# VCode: a Multimodal Coding Benchmark with SVG as Symbolic Visual Representation

<div align="center">

<a href="https://csu-jpg.github.io/VCode" target="_blank">
  <img src="https://img.shields.io/badge/Project-Page-brightgreen">
</a>
<a href="https://github.com/CSU-JPG/VCode" target="_blank">
  <img src="https://img.shields.io/badge/Code-GitHub-black">
</a>

</div>

We propose **VCode**: A Novel Perspective for Multimodal Coding.

![Overview](./assets/teaser.png)

**VCoder** is a framework that augments VLMs as strong multimodal coders.

![VCoder Overview](./assets/vcoder.png)

## 📋 Table of Contents

<!--- [📚 Introduction](#-introduction)-->

- [🛠️ Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
- [🔮 Evaluation](#-evaluation)

---

## 🛠️ Installation

**Environment**

```bash
git clone -b main --single-branch https://github.com/CSU-JPG/VCode.git
cd VCode
conda env create -f environment.yaml
conda activate vcode
```

---

## 🚀 Quick Start

### VCode-suite

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


#### ⚙️ Usage

1️⃣ Generate and Render SVGs

`pipeline.sh` orchestrates the full image-to-SVG-to-render workflow.
It can connect to different generation modules — `img2svg`, `img2text2svg`, or `img2svgthinking` — to convert images into SVGs, then filter and render them into pixel images.

```bash
chmod +x pipeline.sh
./pipeline.sh
```

2️⃣ Optimize Generated SVGs

`revision_pipeline.sh` automates the revision and optimization process.
It takes the previously generated SVGs (`generated_svgs/`) and rendered images (`generated_imgs/`), calls the API-based revision module, and outputs the optimized SVGs and renders to `optimized_svgs/` and `optimized_imgs/`.

```bash
chmod +x revision_pipeline.sh
./revision_pipeline.sh
```

#### 3️⃣ Run Scripts Independently

Both generation and revision scripts can be executed independently for flexible and customized workflows.

Each core generation script — `img2svg.py`, `img2text2svg.py`, `img2svgthinking.py`, and `img2svg-w-visual-tool.py` — can directly convert input images into SVG code.
Similarly, `revision.py` can be run independently to optimize previously generated SVGs through visual feedback.

---

##### Run `img2svg.py`

```bash
python vcode-suite/img2svg.py \
  /path/to/input_images \
  ./generated_svgs \
  --model gpt-5 \
  --base-url https://api.deepinfra.com/v1/openai \
  --api-key sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --max-tokens 16384
```

| Argument            | Type | Default                               | Description                                               |
| ------------------- | ---- | ------------------------------------- | --------------------------------------------------------- |
| `images_folder`     | str  | —                                     | Path to the input folder containing image files.          |
| `svg_output_folder` | str  | —                                     | Directory to save the generated SVG files.                |
| `--model`           | str  | `gpt-5`                               | API model name used for conversion.                       |
| `--base-url`        | str  | `https://api.deepinfra.com/v1/openai` | Base URL of the API endpoint.                             |
| `--api-key`         | str  | Required                              | API key for authentication.                               |
| `--sleep`           | int  | `5`                                   | Seconds to wait between consecutive API calls.            |
| `--max-tokens`      | int  | `16384`                               | Maximum number of tokens allowed in the model’s response. |

---

##### Run `revision.py`

```bash
python vcode-suite/revision.py \
  --svg-folder ./generated_svgs \
  --original-folder ./input_images \
  --rendered-folder ./generated_imgs \
  --output-folder ./optimized_svgs \
  --analysis-folder ./visual_analysis \
  --base-url https://api.openai.com/v1 \
  --api-key sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --model gpt-5 \
  --max-tokens 16384
```

| Argument            | Type | Default                       | Description                                             |
| ------------------- | ---- | ----------------------------- | ------------------------------------------------------- |
| `--svg-folder`      | str  | —                             | Root directory containing the SVG files to optimize.    |
| `--original-folder` | str  | —                             | Directory of the original reference images.             |
| `--rendered-folder` | str  | —                             | Directory of rendered images corresponding to the SVGs. |
| `--output-folder`   | str  | —                             | Directory to save the optimized SVG files.              |
| `--analysis-folder` | str  | —                             | Directory to save visual comparison and analysis txts.  |
| `--base-url`        | str  | `https://tao.plus7.plus/v1`   | Base URL of the API endpoint.                           |
| `--api-key`         | str  | `os.getenv('OPENAI_API_KEY')` | API key.                                                |
| `--model`           | str  | `claude-4-opus`               | Model used for revision.                                |
| `--max-tokens`      | int  | `16384`                       | Maximum tokens allowed in the model response.           |

> 💡 **Tip:**
> The `revision.py` script refines existing SVGs based on visual comparison feedback, while generation scripts (`img2svg.py`, `img2text2svg.py`, `img2svgthinking.py`, `img2svg-w-visual-tool.py`) create SVGs from input images_folder.
> You can flexibly mix and match these tools depending on your pipeline needs.

---

## 🔮 Evaluation

**Step 1 — Generate `generated_imgs/` for all three datasets**

Use the VCode-suite pipeline (or standalone scripts) to render images for each dataset.
Original images are already in `data/`:

- **MM-Vet:** `data/mm-vet/images`
- **CV-Bench:** `data/cv-bench/img`
- **MMMU:** `data/mmmu/mmmu_dev_processed_single_img_subset`

Running your pipeline will produce, per dataset, a folder like:

```
generated_svgs/
generated_imgs/  ← used by the evaluators
```

---

**Step 2 — Run each dataset’s evaluator**

Each evaluator is a shell script under `subtask/…`. They all follow the same usage:

```bash
chmod +x subtask/mm-vet/mmvet_eval.sh
./subtask/mm-vet/mmvet_eval.sh
```

```bash
chmod +x subtask/cv-bench/cvbench_eval.sh
./subtask/cv-bench/cvbench_eval.sh
```

```bash
chmod +x subtask/mmmu/mmmu_eval.sh
./subtask/mmmu/mmmu_eval.sh
```

These scripts will read your `generated_imgs/` and compute scores.

> 💡 **Reference:** For directory organization and example script configuration, see **`example_results/`** (it shows a working layout you can mirror).
