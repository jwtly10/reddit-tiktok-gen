"""
Provides a command-line utility script to nicely format user imported videos ready for the app to pick up and process.
It will crop and compress the video to a suitable size for Tiktok.
"""

from app.utils.ffmpeg import resize_video, compress_video, FFMpegProcessingError

import sys
import os

## check for .mp4 extension
if len(sys.argv) != 2:
    print("Usage: python -m scripts.add_new_background_video.py")
    print(
        "This script will format and compress uncropped mp4 videos for usage in the app. Your new video will be saved in the assets/background_video directory."
    )
    sys.exit(1)

if sys.argv[1].endswith(".mp4"):
    print("Formatting video...")
    file_name = os.path.basename(sys.argv[1])
    output_dir = os.path.join("assets", "background_videos")
    formatted_file = os.path.join(output_dir, file_name)
    os.makedirs(output_dir, exist_ok=True)
    try:
        print("This may take a while...")
        resize_video(sys.argv[1], formatted_file)
    except FFMpegProcessingError as e:
        print(f"Error: {e.stderr}")
        sys.exit(1)

    print(f"Video formatted and saved to {formatted_file}")


else:
    print("Only .mp4 background videos are supported. Exiting...")
    sys.exit(1)
