# Fine-tuning on EgoBlind Dataset

This repository provides comprehensive implementations for fine-tuning three state-of-the-art multimodal models on the EgoBlind dataset. Each model is optimized for different use cases and performance requirements.

## 🤖 Supported Models

- **InternVL2.5-8B**
- **Qwen2.5-VL-7B**
- **LLaVA-OV-7B**

---

## 📋 System Requirements

Before starting, ensure your system meets the following requirements:

- **GPU**: At least 2×80GB GPUs required
- **Python**: Version 3.9-3.10

---

## 🔧 Data Preprocessing

### Step 1: Video Data Preparation

1. Download `video.zip` from [Google Drive](https://drive.google.com/drive/folders/1G8oXYJmkA-6WQgTLtDw6coyM26z84sJu)
2. Extract the contents to your workspace directory
3. Split videos to match question timestamps:

```bash
pip install moviepy
python video_split.py --csv train.csv --video_dir video/
```

### Step 2: Dataset Configuration

Convert the dataset to model-specific formats:

#### ➤ InternVL2.5

```bash
python convert.py --csv train.csv --output data/internvl.jsonl --model_type internvl
```

*Note: Update the `annotation` path in `internvl/shell/data/internvl_1_2_finetune.json` to point to `internvl.jsonl`*

#### ➤ Qwen2.5-VL

```bash
python convert.py --csv train.csv --output data/qwen.json --model_type qwen
```

*Note: Update the `annotation_path` in `qwenvl/qwenvl/data/__init__.py` to point to `qwen.json`*

#### ➤ LLaVA-OV

```bash
python convert.py --csv train.csv --output data/llava.json --model_type llava
```

*Note: Update the `json_path` in `llava_ov/scripts/train/llava.yaml` to point to `llava.json`*

---

## ⚙️ Installation & Setup

### 🔹 InternVL2.5

1. Navigate to the InternVL directory and create the environment:

   ```bash
   cd internvl
   conda env create -f environment.yml
   conda activate internvl
   ```

2. Install Flash Attention for optimized training:

   ```bash
   pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.7.3/flash_attn-2.7.3+cu12torch2.5cxx11abiFALSE-cp39-cp39-linux_x86_64.whl
   ```

3. Download the [InternVL2.5-8B pre-trained model](https://huggingface.co/OpenGVLab/InternVL2_5-8B) to `models/` directory

---

### 🔹 Qwen2.5-VL

1. Navigate to the Qwen directory and create the environment:

   ```bash
   cd qwenvl
   conda env create -f environment.yml
   conda activate qwen
   ```

2. Install Flash Attention:

   ```bash
   pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.7.4.post1/flash_attn-2.7.4.post1+cu12torch2.6cxx11abiFALSE-cp310-cp310-linux_x86_64.whl
   ```

3. Download the [Qwen2.5-VL-7B-Instruct pre-trained model](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct) to `models/` directory

---

### 🔹 LLaVA-OV

1. Navigate to the LLaVA-OV directory and create the environment:

   ```bash
   cd llava_ov
   conda env create -f environment.yml
   conda activate llava
   ```

2. Install the package in development mode:

   ```bash
   pip install --upgrade pip  # Enable PEP 660 support
   pip install -e ".[train]"
   ```

3. Install Flash Attention:

   ```bash
   pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.7.3/flash_attn-2.7.3+cu12torch2.1cxx11abiFALSE-cp310-cp310-linux_x86_64.whl
   ```

4. Download the [LLaVA OneVision Qwen2-7B-OV pre-trained model](https://huggingface.co/lmms-lab/llava-onevision-qwen2-7b-ov) to `models/` directory

---

## 🎯 Fine-tuning Process

### ✨ InternVL2.5

1. Start the fine-tuning process:

   ```bash
   cd internvl
   GPUS=2 PER_DEVICE_BATCH_SIZE=2 sh shell/internvl2.5/2nd_finetune/internvl2_5_8b_dynamic_res_2nd_finetune_lora.sh
   ```

2. **LoRA Weight Merging**: After training, merge LoRA weights with the base model:

   ```bash
   python merge_lora.py work_dirs/internvl_chat_v2_5/8b_finetune_lora ../models_ft/internvl_v2_5_8b_finetune_lora
   ```

3. **AutoModel Integration**: Copy necessary configuration files:

   ```bash
   cp ../models/InternVL2_5-8B/*.py ../models_ft/internvl_v2_5_8b_finetune_lora/
   ```

The fine-tuned model is now ready for inference and deployment using AutoModel.

---

### ✨ Qwen2.5-VL

Execute the fine-tuning script:

```bash
cd qwenvl
sh scripts/sft_7b.sh
```

The fine-tuned model will be automatically saved to `../models_ft/qwen2_5vl_finetune` and is ready for immediate use.

---

### ✨ LLaVA-OV

1. **Pre-training Configuration**: Modify the model type in the configuration file:

   ```bash
   # Change model_type from "llava" to "qwen2" in:
   # models/llava-onevision-qwen2-7b-ov/config.json
   ```

2. **Start Fine-tuning**:

   ```bash
   cd llava_ov
   sh scripts/train/finetune_ov_lora.sh
   ```

3. **LoRA Weight Merging**: Merge the trained LoRA weights:

   ```bash
   python scripts/merge_lora_weights.py \
     --model-base ../models/llava-onevision-qwen2-7b-ov/ \
     --model-path checkpoints/llava-onevision-google_siglip-so400m-patch14-384-Qwen2-7B-Instruct-ov_stage_am9_lora/ \
     --save-model-path ../models_ft/llava_ov_finetune/
   ```

The final model will be saved to `../models_ft/llava_ov_finetune` and is ready for deployment.

---

## 🙏 Acknowledgements

This project builds upon the outstanding work of the following open-source projects:

- **[InternVL](https://github.com/OpenGVLab/InternVL)**: For providing the InternVL2.5 model and training frameworks
- **[Qwen2.5-VL](https://github.com/QwenLM/Qwen2.5-VL)**: For providing the Qwen2.5-VL model and training frameworks
- **[LLaVA-NeXT](https://github.com/LLaVA-VL/LLaVA-NeXT)**: For providing the LLaVA OneVision model and training frameworks

We sincerely thank these communities for their invaluable contributions to the field of multimodal AI.
