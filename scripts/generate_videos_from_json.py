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

from app.service.generate import generate_video_from_content

import logging
from app.utils.logger import log

from app.utils.ffmpeg import FFMpegProcessingError

# Comment this line to see debug logs, can help with debugging, should unhandled exceptions occur
# log.setLevel(logging.ERROR)


def print_progress(total, time_taken):
    print(f"+{'-'*48}+")
    print(f"| {'Progress':15} | {total}/{total} video(s) |")
    print(f"| {'Time Elapsed':15} | {time_taken:.2f} seconds  |")
    print(f"+{'-'*48}+")

async def worker(name, queue):
    while True:
        video_data = await queue.get()
        try:
            print(f"Worker {name} is processing video {video_data['id']}")
            await generate_video_from_content(
                video_data['id'],
                video_data['title'],
                video_data['content'],
                video_data['base_background_video'],
                video_data['output_dir'],
                None,
                video_data['config_preset']
            )
        except Exception as e:
            print(f"Error processing video {video_data['id']}: {e}")
        finally:
            queue.task_done()

async def main(import_file_path, output_directory, config_preset, parallel_processes=1):
    # Validate config preset
    if config_preset not in app.config.ffmpeg_config:
        raise ValueError(f"Invalid config preset: {config_preset}")

    # Create output directory
    os.makedirs(output_directory, exist_ok=True)

    # Load video data
    with open(import_file_path, "r") as f:
        videos = json.load(f)["videos"]

    queue = asyncio.Queue()

    start_time = time()
    
    # Create worker tasks
    tasks = []
    for i in range(parallel_processes):
        task = asyncio.create_task(worker(f'Worker-{i}', queue))
        tasks.append(task)

    # Enqueue video processing tasks
    for counter, video in enumerate(videos, start=1):
        if len(video["title"]) > 125:
            print(f"ERROR: Title too long for video {counter}. Max 124 characters.")
            continue

        video_data = {
            'id': counter,
            'title': video['title'],
            'content': video['content'],
            'base_background_video': os.path.join("assets", f"minecraft_background_video_{1}.mp4"),
            'output_dir': os.path.join(output_directory, str(counter)),
            'config_preset': config_preset
        }
        await queue.put(video_data)

    # Wait for all tasks to be completed
    await queue.join()

    # Cancel worker tasks
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

    print_progress(len(videos), time() - start_time)
    # Clean up some of these files, other than final.mp4
    for file in os.listdir(output_directory):
        if file != "final.mp4":
            os.remove(os.path.join(output_directory, file))

    counter += 1

    

if __name__ == "__main__":
    import app.config

    if len(sys.argv) != 5:
        print("Incorrect number of arguments")
        print(
            "Usage: python generate_videos_from_file.py <import_file_path> <output_directory> <config_preset> <parallel_processes>"
        )
        sys.exit(1)
    else:
        import_file_path = sys.argv[1]
        output_directory = sys.argv[2]
        config_preset = sys.argv[3]
        parallel_processes = int(sys.argv[4])
        print(f"Running with {parallel_processes}")
        asyncio.run(main(import_file_path, output_directory, config_preset, parallel_processes))
