import os
import sys
import json
import ast
import argparse
import requests
import pandas as pd
from tqdm import tqdm

# Replace with your actual OpenAI API key
api_key = 'YOUR_API_KEY'

def parse_args():
    """
    Parse command-line arguments for prediction file and test file paths.
    """
    parser = argparse.ArgumentParser(description="Evaluate question-answer predictions using GPT-4o-mini")
    parser.add_argument("--pred_path", type=str, required=True, help="Path to the prediction .jsonl file")
    parser.add_argument("--test_path", type=str, required=True, help="Path to the test set .csv file")
    return parser.parse_args()


def GPT_Score(key, qa_set, output_dir):
    """
    Call OpenAI API to evaluate if the predicted answer meaningfully matches any correct answers.
    Save the evaluation result as a JSON file per question.
    """
    question = qa_set['q']
    answer0 = qa_set['a0']
    answer1 = qa_set['a1']
    answer2 = qa_set['a2']
    answer3 = qa_set['a3']
    pred = qa_set['pred']

    content_system = (
        "You are an intelligent chatbot designed for evaluating the correctness of generative outputs for question-answer pairs. "
        "Your task is to compare the predicted answer with the correct answer and determine if they match meaningfully. Here's how you can accomplish the task:"
        "------"
        "##INSTRUCTIONS: "
        "- Focus on meaningful matches: Assess whether the predicted answer and the correct answer have a meaningful match, not just literal word-for-word matches.\n"
        "- Criteria for Correctness: The predicted answer is considered correct if it reasonably matches any of the four standard answers, recognizing that synonyms or varied expressions that convey the same meaning are acceptable.\n"
        "- Allow for Paraphrasing: Understand that different wording that conveys the same fundamental idea is valid.\n"
        "- Flexibility in Evaluation: Use judgment to decide if variations in the predicted answer still correctly address the question, even if they do not directly replicate the correct answer's phrasing.\n"
        "Answers should be tailored for blind individuals, avoiding reliance on any visual descriptions."
    )

    content_list = [{
        "type": "text",
        "text": (
            f"Please evaluate the following video-based question-answer pair:\n\n"
            f"Question: {question}\n"
            f"Correct Answer0: {answer0}\n"
            f"Correct Answer1: {answer1}\n"
            f"Correct Answer2: {answer2}\n"
            f"Correct Answer3: {answer3}\n"
            f"Predicted Answer: {pred}\n\n"
            "Provide your evaluation only as a yes/no and score where the score is a float value between 0 and 5, with 5 indicating the highest meaningful match. "
            "Generate the response in the form of a Python dictionary string with keys 'pred' and 'score'. For example: {'pred': 'yes', 'score': 4}."
        )
    }]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": content_system},
            {"role": "user", "content": content_list}
        ],
        "max_tokens": 1000
    }
    
    response_message = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    data = response_message.json()
    if 'choices' not in data:
        print("Fail to get responses from OpenAI. Please ensure to specify the API key!")
        sys.exit()
    first_choice = data['choices'][0]['message']['content']
    response_dict = ast.literal_eval(first_choice)

    result_qa_pair = [response_dict, qa_set]

    with open(os.path.join(output_dir, f"{key}.json"), "w") as f:
        json.dump(result_qa_pair, f)


def calculate_metrics(csv_path, json_path, output_path):
    """
    Calculate per-type and overall evaluation metrics (accuracy, average score).
    Save final metrics as a JSON summary.
    """
    df = pd.read_csv(csv_path)
    id_to_type = df.set_index('question_id')['type'].to_dict()

    with open(json_path, 'r') as f:
        json_data = json.load(f)

    total_score = 0.0
    stats = {}

    for q_id, entries in json_data.items():
        type_ = id_to_type.get(q_id)
        if not type_:
            print(f"Type not found for question ID: {q_id}")
            continue

        type_ = type_.strip().lower().rstrip('.')

        if type_ not in stats:
            stats[type_] = {"total": 0, "yes_count": 0, "score_sum": 0.0}

        entry = entries[0]
        pred = entry.get("pred", "").lower()
        score = float(entry.get("score", 0))

        stats[type_]["total"] += 1
        if pred == "yes":
            stats[type_]["yes_count"] += 1
        stats[type_]["score_sum"] += score
        total_score += score

    result = {}
    for type_, data in stats.items():
        total = data["total"]
        accuracy = data["yes_count"] / total if total else 0.0
        avg_score = data["score_sum"] / total if total else 0.0
        result[type_] = {
            "total": total,
            "accuracy": round(accuracy, 4),
            "average_score": round(avg_score, 4)
        }

    total_yes = sum(d["yes_count"] for d in stats.values())
    total_entries = sum(d["total"] for d in stats.values())
    overall_accuracy = total_yes / total_entries if total_entries else 0
    overall_avg_score = total_score / total_entries if total_entries else 0

    result["total"] = {
        "total": total_entries,
        "accuracy": round(overall_accuracy, 4),
        "average_score": round(overall_avg_score, 4)
    }

    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)


def main():
    args = parse_args()

    # Load prediction and test files
    with open(args.pred_path, encoding='utf-8') as f:
        predictions = [eval(line.strip()) for line in f.readlines()]

    test_df = pd.read_csv(args.test_path)
    test_data = test_df.set_index('question_id').to_dict(orient='index')

    model_name = os.path.basename(args.pred_path).split('.')[0]
    output_dir = f"./{model_name}"
    os.makedirs(output_dir, exist_ok=True)

    # Prepare prediction dictionary and expected output filenames
    prediction_set = {}
    caption_files = []

    for item in predictions:
        qid = item['question_id']
        if qid not in test_data:
            print(f"Warning: Question ID {qid} not found in test data. Skipping...")
            continue

        question_info = test_data[qid]
        prediction_set[qid] = {
            "q": question_info['question'],
            "a0": question_info['answer0'],
            "a1": question_info['answer1'],
            "a2": question_info['answer2'],
            "a3": question_info['answer3'],
            "type": question_info['type'],
            "pred": item['pred']
        }
        caption_files.append(f"{qid}.json")

    completed_files = set(os.listdir(output_dir))

    cnt = 0
    for file in tqdm(caption_files, desc="Evaluating predictions"):
        if file in completed_files:
            print(f"{file} has already been processed.")
            continue

        key = file.split('.')[0]
        qa_set = prediction_set.get(key)
        if qa_set:
            GPT_Score(key, qa_set, output_dir)
            cnt += 1
        else:
            print(f"Warning: No QA data found for key {key}. Skipping...")
    print(f"Evaluating on {cnt} samples ...")
    # Combine individual JSON results into one dictionary
    combined_results = {}
    for fname in os.listdir(output_dir):
        if fname.endswith(".json"):
            with open(os.path.join(output_dir, fname), "r") as f:
                result = json.load(f)
                combined_results[fname.split('.')[0]] = result

    combined_result_path = f"./result_{model_name}.json"
    with open(combined_result_path, "w") as f:
        json.dump(combined_results, f)

    # Calculate and display final evaluation metrics
    metrics_output_path = f"./metrics_{model_name}.json"
    calculate_metrics(args.test_path, combined_result_path, metrics_output_path)

    with open(metrics_output_path, "r") as f:
        final_metrics = json.load(f)

    print("Evaluation Completed!")
    print(json.dumps(final_metrics["total"], indent=2))


if __name__ == "__main__":
    main()
