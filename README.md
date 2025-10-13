# [EgoBlind](https://arxiv.org/abs/2503.08221)
EgoBlind (Accepted to NeurIPS'25 D&B Track) is the first VideoQA dataset collected from real blind people towards egocentric visual assistance. EgoBlind comprises 1,392 videos that record the daily lives of real blind users from a first-person perspective. It also features 5.3K questions directly posed or generated and verified by blind individuals to reflect their in-situation needs for visual assistance under various scenarios.

**Highlights**:
1) EgoBlind videos reflect the real daily life of the blind and the visually-impaired. Both the questions and answers are in-situation, based on the users' personal activities and intentions.
2) We provide well-classified question types and multiple ground-truth answer annotations for better evaluation and analysis, the answers are timestamp-specific to support live QA.
3) GPT-4o and Gemini 2.5 level intelligence can only achieves accuracy of 55%~60%, falling behind human by a whopping ~28%.
4) Our comprehensive analyses elicit three major challenges: ```Egocentric dynamic scene understanding```, ```In-situatin user intention reasoning```, and ```Helpful and reliable answer generation```.
5) A blind-specific prompt consistently benefits answering different types of questions, indicating a data difference between EgoBlind and common VideoQA. 
6) Instruction tuning with EgoBlind training data can remarkablyly improve the open-source model performances (e.g., improving InternVL2.5-8B by 4.6% from 53.5% to 58.1%).

## Data Characteristics
1) Regions of interest are often off-center and not well-focused.
2) Questions reflect user intention in specific situation and may be ambiguous if without considering spatial and temporal contexts.
3) Answers are not only correct to the visual contents but must be helpful to the users.

![EgoBlind](misc/intro.jpg)

## Todo
1. [x] Release finetuning code.

## Data Examples
![EgoBlind](misc/egoblind.jpg)
## Download
We are glad to share that the dataset can be freely used for research purpose, but with [video source](https://drive.google.com/file/d/1Wob42tJ95DL1VvKad7BPc5QIlHtiuttI/view?usp=sharing) being cited for distribution. Please download EgoBlind training set from [Google Driven](https://drive.google.com/drive/folders/1zW8waLCS_8Ay8kOWpCsvF77IeIG9TzOq?usp=sharing), and test set from [Google Driven](https://drive.google.com/drive/folders/1gLcqwKrJcZ7tTbaBI8aWEhPImRdDsGQx?usp=sharing).  

## Evaluation
A random half of the ground-truth answers in the test set are withheld by us, please send a complete prediction file to (junbin@comp.nus.edu.sg) for full evaluation. We provide the evaluation script along with an example full prediction file for testing. Please ensure that you have an OpenAI API key before running the script:
```
python eval.py --pred_path example_pred.jsonl --test_path test_half_release.csv
```
The evaluation may take about 18 minutes, and the results will be saved to metrics_xxx.json and results_xxx.json.
## Benchmarking
| Methods              | LLM                | Res.     | #F      | Tool Use   | Information | Navigation | Safety    | Communication | Resource  | Overall   |
|----------------------|--------------------|----------|---------|------------|-------------|------------|-----------|----------------|-----------|-----------|
| **Human**            | -                  | -        | -       | 70.4 | 87.0  | 83.1 | 91.9 | 94.7     | 96.6 | 87.4 |
| [ShareGPT4Video](https://github.com/ShareGPT4Omni/ShareGPT4Video)   | LLaMA3-8B          | ori        | 2fps    | 25.5 | 32.6  | 20.7 | 43.3 | 38.9  | 28.3 | 32.9 |
| [CogVLM2-Video](https://github.com/THUDM/CogVLM2)   | LLaMA3-8B          | 224²     | 24      | 32.2 | 44.5  | 14.0 | 52.7 | 43.1   | 32.4 | 40.3|
| [Video-LLaMA3](https://github.com/DAMO-NLP-SG/VideoLLaMA3)    | Qwen2.5-7B  | ori  | 1fps    | 53.0 | 51.9  | 38.1 | 50.6 | 41.7 | 50.3 | 49.2 |
| [InternVL2.5-8B](https://github.com/OpenGVLab/InternVL)  | InternLM2.5-Chat-7B| 448²     | 8       | 61.1 | 54.6  | 42.2 | 58.0 | 44.4  | 52.6 | 53.5 |
 [LLaVA-OV](https://github.com/LLaVA-VL/LLaVA-NeXT)        | Qwen2.7B           | 384²     | 16      | 61.1 |  56.4  | 29.5 | **65.8** | **58.3** | 50.9 | 54.5|
| [InternVL2.5-26B](https://github.com/OpenGVLab/InternVL) | InternLM2.5-Chat-20B| 448²    | 8       | **72.5** | 56.9 | 47.4 | 54.1 | 43.1   | 53.2 | 55.0 |
| [MiniCPM-V 2.6](https://github.com/OpenBMB/MiniCPM-o)   | Qwen2-7B           | 384²     | 1fps      | 53.7 | 46.5  | 37.8 | 28.9 | 37.5 | 41.0 | 40.7 |
| [Qwen2.5-VL](https://github.com/QwenLM/Qwen2.5-VL)       | Qwen2.5-7B         | ori      | 1fps    | 51.0 | 50.1  | 28.2 | 48.5 | 43.1  | 38.2 | 45.5|
| [LLaVA-Video](https://github.com/LLaVA-VL/LLaVA-NeXT)     | Qwen2-7B           | 384²     | 1fps    | 44.3 | 53.4  | 32.6 | 62.0 | 50.0    | 49.7 | 51.5 |
| [Video-LLaVA](https://github.com/PKU-YuanGroup/Video-LLaVA)     | Vicuna-7B          | 224²     | 8      | 22.8 | 41.2  | 21.2 | 47.2 | 38.9  | 35.3 | 38.1 |
| [LLaMA-VID](https://github.com/dvlab-research/LLaMA-VID)       | Vicuna-7B          | 224²     | 1fps    | 32.2 | 40.5  | 20.7 | 49.4 | 36.1  | 41.6 | 39.1|
| [VILA1.5](https://github.com/NVlabs/VILA)         | LLaMA3-8B          | 336²     | 8       | 49.7 | 50.5  | 25.9 | 60.6 | 47.2| 41.0 | 48.2|
| Gemini 1.5 Flash     | -                  | ori      | 32       | 72.5 | 54.4 | 43.5 | 50.6| 38.9 | 45.7| 51.8 |
| Gemini 2.0 Flash     | -                  | ori      | 32   | 61.1 | 54.5 | 50.5  | 39.1 | 47.2 | 49.1 | 49.9 |
| Gemini 2.5 Flash     | -                  | ori      | 32   | 67.1 | 57.6 | 47.7 | 57.8 | 47.2 | 50.3 | 56.0 |
| GPT-4o              | -                  | ori      | 32  | 66.4 | **61.2** | **52.6** | 58.8 | 47.2 | **62.4** | **59.3** |
## Result Visualization
![EgoBlind](misc/vis.jpg)

## Cite
```
@article{xiao2025egoblind,
  title={EgoBlind: Towards Egocentric Visual Assistance for the Blind},
  author={Xiao, Junbin and Huang, Nanxin and Qiu, Hao and Tao, Zhulin and Yang, Xun and Hong, Richang and Wang, Meng and Yao, Angela},
  journal={arXiv preprint arXiv:2503.08221},
  year={2025}
}
```

## Notes
The dataset is strictly for research purpose. Please always attach the source links of the videos for distribution if available.
