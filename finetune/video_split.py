import csv
from pathlib import Path
from tqdm import tqdm
from moviepy.video.io.VideoFileClip import VideoFileClip
import argparse

def data_process(row, video_dir):

    video_name = Path(video_dir) / f"{row['video_name']}.mp4"
    start_time = max(row['start-time/s'] / 1000, 0.1) # Ensure start time is at least 0.1 seconds to avoid errors

    with VideoFileClip(video_name) as video:
        clipped_video = video.subclipped(0, start_time)
        clipped_video_file_name = f"./video_clip/{row['question_id']}.mp4"
        if video.audio is not None:
            clipped_video.write_videofile(clipped_video_file_name, codec="libx264", audio_codec="aac")
        else:
            clipped_video.write_videofile(clipped_video_file_name, codec="libx264", audio=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process video files based on CSV input.")
    parser.add_argument("--csv", type=str, default="train.csv", help="Path to the input CSV file.")
    parser.add_argument("--video_dir", type=str, default="video/", help="Directory containing video files.")
    
    args = parser.parse_args()

    Path("./video_clip").mkdir(parents=True, exist_ok=True)
    
    # Read the CSV file
    with open(args.csv, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        for row in tqdm(csv_reader, desc="Processing videos"):
            data_process(row, args.video_dir)
