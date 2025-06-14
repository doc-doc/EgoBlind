import requests
import os
import argparse
import json
import ast
from multiprocessing.pool import Pool
from tqdm import tqdm

api_key='API_KEY' #Replace with your OpenAI key
def parse_args():
    parser = argparse.ArgumentParser(description="question-answer-evaluation-using-gpt-4o-mini")
    parser.add_argument("--num_tasks", default=80, type=int, help="Number of splits.")
    args = parser.parse_args()
    return args


def annotate(prediction_set, caption_files, output_dir, args):
    """
    Evaluates question and answer pairs using GPT-4o-mini
    Returns a score for correctness.
    """
    # Set the OpenAI API key.
    for file in caption_files:
        key = file[:-5] # Strip file extension
        qa_set = prediction_set[key]
        question = qa_set['q']
        answer0 = qa_set['a0']
        answer1 = qa_set['a1']
        answer2 = qa_set['a2']
        answer3 = qa_set['a3']
        pred = qa_set['pred']
        print(pred)
            # Compute the correctness score
        content_system =("You are an intelligent chatbot designed for evaluating the correctness of generative outputs for question-answer pairs. "
                        "Your task is to compare the predicted answer with the correct answer and determine if they match meaningfully. Here's how you can accomplish the task:"
                        "------"
                        "##INSTRUCTIONS: "
                        "- Focus on meaningful matches: Assess whether the predicted answer and the correct answer have a meaningful match, not just literal word-for-word matches.\n"
                        "- Criteria for Correctness:The predicted answer is considered correct if it reasonably matches any of the four standard answers, recognizing that synonyms or varied expressions that convey the same meaning are acceptable.\n"
                        "- Allow for Paraphrasing: Understand that different wording that conveys the same fundamental idea is valid. Evaluate if the essence of the predicted answer captures the core information of the correct answer.\n"
                        "- Flexibility in Evaluation: Use judgment to decide if variations in the predicted answer still correctly address the question, even if they do not directly replicate the correct answer's phrasing.for example:when the correct answer is 'Left front',Predicted Answer:' About ten meters to your left front',these two answers match.\n"                        
                        "Your responses should be tailored specifically for blind individuals, ensuring that they do not rely on any visual elements, diagrams, or imagery for understanding. All explanations must be conveyed clearly through descriptive text, focusing on concepts, structures, and relationships that can be understood without the need for visual cues. Answers that include references to visual content or require visual interpretation will not be considered correct.bad example:pred:Follow the sign pointing right for tickets."
                        )
        content_list = [
                    {
                     "type": "text",
                     "text":
                     "You are an intelligent chatbot designed for evaluating the correctness of generative outputs for question-answer pairs. "
                        "Your task is to compare the predicted answer with the correct answer and determine if they match meaningfully. Here's how you can accomplish the task:"
                        "------"
                        "INSTRUCTIONS: "
                        "- Focus on meaningful matches: Assess whether the predicted answer and the correct answer have a meaningful match, not just literal word-for-word matches.\n"
                        "- Criteria for Correctness:The predicted answer is considered correct if it reasonably matches any of the four standard answers, recognizing that synonyms or varied expressions that convey the same meaning are acceptable.\n"
                        "- Allow for Paraphrasing: Understand that different wording that conveys the same fundamental idea is valid. Evaluate if the essence of the predicted answer captures the core information of the correct answer.\n"
                        "- Flexibility in Evaluation: Use judgment to decide if variations in the predicted answer still correctly address the question, even if they do not directly replicate the correct answer's phrasing.for example:when the correct answer is 'Left front',Predicted Answer:' About ten meters to your left front',these two answers match.\n"
                        "Please evaluate the following video-based question-answer pair:\n\n"
                        f"Question: {question}\n"
                        f"Correct Answer0: {answer0}\n"
                        f"Correct Answer1: {answer1}\n"
                        f"Correct Answer2: {answer2}\n"
                        f"Correct Answer3: {answer3}\n"
                        f"Predicted Answer: {pred}\n\n"
                        "Provide your evaluation only as a yes/no and score where the score is an float value between 0 and 5, with 5 indicating the highest meaningful match. "
                        "Please generate the response in the form of a Python dictionary string with keys 'pred' and 'score', where value of 'pred' is  a string of 'yes' or 'no' and value of 'score' is in INT, not STRING."
                        "DO NOT PROVIDE ANY OTHER OUTPUT TEXT OR EXPLANATION. Only provide the Python dictionary string. "
                        "For example, your response should look like this: {'pred': 'yes', 'score': 4}."
                }
            ]
        headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    }

        payload = {
                        "model": "gpt-4o-mini",
                        "messages": [
                            {
                                "role": "system",
                                "content": content_system
                            },
                            {
                                "role": "user",
                                "content": content_list
                            }
                        ],
                        "max_tokens": 1000,
                        #"stream": True
                    }
        # Convert response to a Python dictionary.
        response_message = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        data = response_message.json()
        first_choice = data['choices'][0]['message']['content']
        response_dict = ast.literal_eval(first_choice)
        result_qa_pair = [response_dict, qa_set] # 将 response_dict 和原始的问答对 qa_set 组成一个列表 result_qa_pair。

        # Save the question-answer pairs to a json file.
        with open(f"{output_dir}/{key}.json", "w") as f:
            json.dump(result_qa_pair, f)

def append_to_txt(video_name, content, filename="output.txt"):
    """
    将生成的内容追加保存到TXT文件。

    :param video_name: 视频名称。
    :param content: GPT生成的内容。
    :param filename: 保存内容的文件名。
    """
    try:
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(f"video_name: {video_name}\n")
            file.write(f"content: {content}\n")
            file.write("\n")  # 添加换行符分隔每次写入的内容
        print(f"Output successfully appended to {filename}")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")

def main():
    """
    Main function to control the flow of the program.
    """
    # Parse arguments.
    model = 'internvl2_5-8B'
    args = parse_args()

    file = open(f"{model}.jsonl", encoding='utf-8')
    new_pred_contents = [eval(i.strip()) for i in file.readlines()]
    # Generating list of id's and corresponding files
    id_list = [x['question_id'] for x in new_pred_contents] 
    caption_files = [f"{id}.json" for id in id_list] 

    output_dir = f"./{model}"
    # Generate output directory if not exists.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Preparing dictionary of question-answer sets
    prediction_set = {}
    for sample in new_pred_contents:
        id = sample['question_id']
        question = sample['question']
        answer0 = sample['answer0']
        answer1 = sample['answer1']
        answer2 = sample['answer2']
        answer3 = sample['answer3']
        type = sample['type']
        pred = sample['pred']
        
        qa_set = {"q": question, "a0": answer0, "a1": answer1,"a2": answer2,"a3": answer3, "pred": pred,"type":type}
        prediction_set[id] = qa_set
        print(qa_set)

    num_tasks = args.num_tasks

    # While loop to ensure that all captions are processed.
    while True:
        try:
            # Files that have not been processed yet.
            completed_files = os.listdir(output_dir)
            print(f"completed_files: {len(completed_files)}")

            # Files that have not been processed yet.
            incomplete_files = [f for f in caption_files if f not in completed_files]
            print(f"incomplete_files: {len(incomplete_files)}")

            # Break the loop when there are no incomplete files
            if len(incomplete_files) == 0:
                break
            if len(incomplete_files) <= num_tasks:
                num_tasks = len(incomplete_files)

            # Split tasks into parts.
            part_len = len(incomplete_files) // num_tasks
            all_parts = [incomplete_files[i:i + part_len] for i in range(0, len(incomplete_files), part_len)]
            task_args = [(prediction_set, part, output_dir, args) for part in all_parts]

            # Use a pool of workers to process the files in parallel.
            with Pool() as pool: # 创建一个进程池 pool
                pool.starmap(annotate, task_args) # 对于 task_args 中的每个元素,都会调用 annotate 函数,并传入该元素作为参数。这些任务会被并行处理,以利用多核 CPU 的优势,提高处理速度。

        except Exception as e:
            print(f"Error: {e}")

    # Combine all the processed files into one
    combined_contents = {}
    json_path = f"./result_{model}.json"

    # Iterate through json files
    for file_name in os.listdir(output_dir):
        if file_name.endswith(".json"):
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, "r") as json_file:
                content = json.load(json_file)
                combined_contents[file_name[:-5]] = content

    # Write combined content to a json file
    with open(json_path, "w") as json_file:
        json.dump(combined_contents, json_file)
    print("All evaluation completed!")

    # Calculate average score and accuracy
    score_sum = 0
    count = 0
    yes_count = 0
    no_count = 0
    for key, result in tqdm(combined_contents.items()):
        try:
            # Computing score
            count += 1
            score = result[0]['score']
            score_sum += score

            # Computing accuracy
            pred = result[0]['pred']
            if "yes" in pred.lower():
                yes_count += 1
            elif "no" in pred.lower():
                no_count += 1
        except:
            print(result)

    average_score = score_sum / count
    accuracy = yes_count / (yes_count + no_count)
    print("Yes count:", yes_count)
    print("No count:", no_count)
    print("Accuracy:", accuracy)
    print("Average score:", average_score)


if __name__ == "__main__":
    main()

