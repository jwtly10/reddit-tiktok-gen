"""
Utility script to be able to load a JSON with a list of videos, and generate all of them.
Makes for easy content creation, but note
1. THis is very CPU intensive
2. This will cost you money

Error handling here is minimal, as its expected to be run by developers, who can handle errors themselves (errors will be due to inputs rather than the code itself)
"""

import os
from time import time
import sys
import json
import asyncio
from random import randrange

import app.config

from app.service.generate import generate_video_from_content

import logging
from app.utils.logger import log

from app.utils.ffmpeg import FFMpegProcessingError

# Comment this line to see debug logs, can help with debugging, should unhandled exceptions occur
log.setLevel(logging.ERROR)


def print_progress(current, total, time_taken):
    print(f"+{'-'*48}+")
    print(f"| {'Progress':15} | {current}/{total} video(s) |")
    print(f"| {'Time Elapsed':15} | {time_taken:.2f} seconds  |")
    print(f"+{'-'*48}+")


async def main(import_file_path, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    with open(import_file_path, "r") as f:
        videos = json.load(f)["videos"]

    counter = 1
    start_time = time()
    print(len(videos))
    for video in videos:
        print("Generating video", counter, "of", len(videos))
        id = counter

        if len(video["title"]) > 125:
            print("ERROR: Title is too long. Max 124 Characters.")
            counter += 1
            continue

        print(f"Video Title: {video['title']}")
        print(f"Video Content: {video['content']}")

        title = video["title"]
        content = video["content"]
        base_background_video = os.path.join(
            "assets", f"minecraft_background_video_{randrange(1)}.mp4"
        )

        output_dir = os.path.join(output_directory, str(id))
        os.makedirs(output_dir, exist_ok=True)

        await generate_video_from_content(
            id, title, content, base_background_video, output_dir
        )

        print_progress(counter, len(videos), time() - start_time)

        # Clean up some of these files, other than final.mp4
        for file in os.listdir(output_dir):
            if file != "final.mp4":
                os.remove(os.path.join(output_dir, file))

        counter += 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python generate_videos_from_file.py <import_file_path> <output_directory>"
        )
    else:
        import_file_path = sys.argv[1]
        output_directory = sys.argv[2]
        try:
            asyncio.run(main(import_file_path, output_directory))
        except FFMpegProcessingError as e:
            log.error(str(e.stderr))
            sys.exit(1)
        except Exception as e:
            log.error(str(e))
