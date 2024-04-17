from app.utils.logger import log
from app.utils.ffmpeg import (
    get_audio_duration,
    buffer_audio,
    loop_video_to_audio,
    concatenate_audios,
    delay_srt,
    embed_srt_and_audio,
    overlay_image_on_video,
    get_video_dimensions,
    resize_image,
    FFMpegProcessingError,
)
from app.utils.background_video import get_random_chunk_from_video
from app.utils.gentle_aligner import GentleAligner
from app.utils.image_generator import generate_title_image
import os
import app.config

"""
This is a utility script to easily generate a video for testing purposes.
Uses the gentle aligner docker image and ffmpeg, but no other services.
By default it uses media files based off of the test fixtures, so you can change the path to your own generated media files.
"""

content = """
I'll keep it brief because it's so timely. Am I the asshole because it's Father's Day and all I wanted to do was spend time alone in the backyard, smoking a cigar, and listening to music/podcasts by myself? I recognize without kids, I am not a subject of this holiday, but my wife and kids are giving the pass and I'm taking it. Yet part of me still wonders...
"""
title = """
AITA for wanting to be alone on Father's Day?
"""
output_dir = os.path.join("scripts", "output")
os.makedirs(output_dir, exist_ok=True)
base_background_video = os.path.join("assets", "minecraft_background_video_1.mp4")

test_dir = os.path.join("tests", "fixtures", "integration", "service", "generate")

try:
    # Mocking the generation of audio files
    pre_content_audio = os.path.join(test_dir, "pre_content.mp3")
    pre_title_audio = os.path.join(test_dir, "pre_title.mp3")

    # The rest should 'just work'
    content_audio = os.path.join(output_dir, "content.mp3")
    buffer_audio(pre_content_audio, "END", 1, content_audio)

    pre_title_audio_duration = get_audio_duration(pre_title_audio)
    title_audio = os.path.join(output_dir, "title.mp3")
    buffer_audio(pre_title_audio, "END", 1, title_audio)
    title_audio_duration = get_audio_duration(title_audio)

    gentle_aligner = GentleAligner()
    aligned_text = gentle_aligner.generate_aligned(content, content_audio)

    srt_file = os.path.join(output_dir, "content.srt")
    gentle_aligner.generate_srt(aligned_text, srt_file)

    title_image = os.path.join(output_dir, "title_image.png")
    generate_title_image(title_image, title)

    video_audio = os.path.join(output_dir, "video.mp3")
    concatenate_audios(title_audio, content_audio, video_audio)
    total_video_audio_length = get_audio_duration(video_audio)

    background_video = os.path.join(output_dir, "background.mp4")
    get_random_chunk_from_video(base_background_video, 60, background_video)

    looped_background_video = os.path.join(output_dir, "looped_background.mp4")
    loop_video_to_audio(
        total_video_audio_length, background_video, looped_background_video
    )
    video_width = get_video_dimensions(looped_background_video)[0]

    resized_title_image = os.path.join(output_dir, "resized_title_image.png")
    resize_image(title_image, video_width, resized_title_image)

    overlayed_video = os.path.join(output_dir, "overlayed.mp4")
    overlay_image_on_video(
        looped_background_video,
        resized_title_image,
        pre_title_audio_duration,
        overlayed_video,
    )

    delayed_srt_file = os.path.join(output_dir, "delayed_content.srt")
    delay_srt(srt_file, title_audio_duration, delayed_srt_file)

    final_video = os.path.join(output_dir, "final.mp4")
    embed_srt_and_audio(overlayed_video, video_audio, delayed_srt_file, final_video)

    log.info(f"Final video generated at {final_video}")

except FFMpegProcessingError as e:
    log.error(f"FFMpegProcessingError: {e}")
