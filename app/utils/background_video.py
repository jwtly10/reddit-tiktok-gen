import math
import sys
import os
import random

from app.utils.ffmpeg import get_video_duration, split_video, split_video_at_time

from app.utils.logger import log


def get_random_chunk_from_video(
    video_path: str, duration: float, output_path: str, config_preset: str = "default"
):
    """
    Extracts a random chunk of the specified duration from a video.

    Args:
        video_path (str): The path of the video file to extract the chunk from.
        duration (float): The duration of the chunk to extract.
        output_path (str): The path where the extracted chunk will be saved.
        config_preset (str): The ffmpeg configuration preset to use.
    """

    log.info(f"Extracting a random {duration} second clip from {video_path}")

    total_duration = get_video_duration(video_path)
    if total_duration <= duration:
        raise ValueError(
            "The video is too short to extract a clip of the desired length"
        )

    max_start = math.ceil(total_duration - duration)
    random_start = random.randint(0, max_start)

    start_hours = random_start // 3600
    start_minutes = (random_start % 3600) // 60
    start_seconds = random_start % 60
    start_time = f"{start_hours:02}:{start_minutes:02}:{start_seconds:02}"

    log.info(f"Extracting a random {duration} second clip from {video_path}")

    split_video_at_time(video_path, start_time, duration, output_path, config_preset)


def split_video_into_chunks(
    video_path: str, into: float, output_path: str, file_name: str
):
    """
    Splits a background video into multiple chunks.

    Args:
        video_path (str): The path of the video file to be split.
        into (float): The number of parts to split the video into.
        output_path (str): The path where the split video chunks will be saved.
        file_name (str): The base name for the split video chunks.
    """
    log.info(f"Splitting video {video_path} into {into} parts")

    video_duration = get_video_duration(video_path)
    duration_of_chunk = math.ceil(video_duration / into)

    log.debug(f"Video duration: {video_duration}")
    log.debug(f"Duration of each chunk: {duration_of_chunk}")

    file_name_template = f"{output_path}/{file_name}%01d.mp4"

    split_video(video_path, duration_of_chunk, file_name_template)


if __name__ == "__main__":
    from app.utils.logger import log

    if sys.argv[1] == "random_chunk":
        video_path = sys.argv[2]
        duration = float(sys.argv[3])
        output_path = sys.argv[4]

        get_random_chunk_from_video(video_path, duration, output_path)

    if sys.argv[1] == "split_into":
        video_path = sys.argv[2]
        into = float(sys.argv[3])
        output_path = sys.argv[4]
        file_name = sys.argv[5]

        os.makedirs(output_path, exist_ok=True)

        split_video_into_chunks(video_path, into, output_path, file_name)
