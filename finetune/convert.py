import csv
import json
from pathlib import Path
import argparse

def convert_csv(csv_path, output_path, model_type):

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    id_counter = 0
    all_records = []
    
    with open(csv_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        for row in csv_reader:
            video_name = row['question_id']
            prompt = (
                "I will provide you with a video each time and one question; "
                "These questions are all questions raised by the blind person in the video from his own first-person perspective in the current scene. "
                "Your task is to answer the blind person's question which was posed in the last frame of the video. "
                "The answer needs to be based on the content of the picture and the objective characteristics that the blind person cannot see. "
                "If the question cannot be answered, you can say I don't know. "
                "Do not include Chinese characters in your response. "
                f"The question is: {row['question']}"
            )
            
            # Determine media tag and video path
            media_tag = "<image>" if model_type == "llava" else "<video>"
            video_path = f"{video_name}.mp4"

            for i in range(4):  # Process all possible answers
                answer_key = f'answer{i}'
                answer = row.get(answer_key, '').strip()
                
                if answer:
                    conversation = [
                        {"from": "human", "value": f"{media_tag}\n{prompt}"},
                        {"from": "gpt", "value": answer}
                    ]
                    
                    # Build the conversation record
                    record = {"conversations": conversation}

                    # Add video path
                    record["video"] = video_path

                    # Add ID
                    if model_type in ["llava", "internvl"]:
                        record_id = id_counter if model_type == "internvl" else str(id_counter)
                        record["id"] = record_id

                    # Add data source (only llava requires)
                    if model_type == "llava":
                        record["data_source"] = "egoblind"
                    
                    all_records.append(record)
                    id_counter += 1
    
    # Write output file based on model type
    if model_type == "internvl":
        with open(output_path, 'w', encoding='utf-8') as jsonl_file:
            for record in all_records:
                jsonl_file.write(json.dumps(record, ensure_ascii=False) + '\n')
    else:
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(all_records, json_file, ensure_ascii=False, indent=2)
    
    print(f"Conversion completed. {id_counter} records written to {output_path} for {model_type}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert CSV to JSON/JSONL format for different vision-language models"
    )
    parser.add_argument("--csv", type=str, required=True, help="Input CSV file path")
    parser.add_argument("--output", type=str, required=True, help="Output file path")
    parser.add_argument("--model_type", type=str, required=True, 
                        choices=["llava", "qwen", "internvl"], help="Target model type")
    
    args = parser.parse_args()
    
    convert_csv(args.csv, args.output, args.model_type)