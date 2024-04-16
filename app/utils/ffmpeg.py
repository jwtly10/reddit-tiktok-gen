import ffmpeg
import math
import os

from typing import cast

from app.utils.logger import log


class FFMpegProcessingError(Exception):
    def __init__(self, message, stderr=None):
        super().__init__(message)
        self.stderr = stderr


def resize_video(video_path: str, output_path: str):
    """
    Resize a video to maintain a 16:9 aspect ratio on height.

    Args:
    video_path (str): The path to the input video file.
    output_file_path (str): The path to the output resized video file.

    Raises:
        FFMpegProcessingError: If an error occurs during the FFmpeg command execution.
    """

    log.info("Resizing video...")
    log.debug("Video path: %s", video_path)
    log.debug("Output file path: %s", output_path)

    width, height = get_video_dimensions(video_path)
    log.debug("Video dimensions: %dx%d", width, height)
    target_width = min(width, height * 9 // 16)
    target_height = height

    try:
        (
            ffmpeg.input(video_path)
            .filter("crop", target_width, target_height)
            .output(output_path, vcodec="libx264", acodec="copy", preset="ultrafast")
            .global_args("-loglevel", "error")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        raise FFMpegProcessingError(
            "Error during resize_video ffmpeg command", stderr=e.stderr
        )


def split_video_at_time(
    video_path: str, start_time: str, duration: float, output_path: str
):
    """
    Split a video at a specific time and save the segment as a new video file.

    Args:
    video_path (str): The path to the input video file.
    start_time (str): The time in HH:MM:SS format to start the split.
    duration (float): The duration of the segment in seconds.
    output_path (str): The path to save the output video file.

    Raises:
        FFMpegProcessingError: If an error occurs during the FFmpeg command execution.
    """

    log.info("Splitting video at time...")
    log.debug("Video path: %s", video_path)
    log.debug("Start time: %s", start_time)
    log.debug("Duration: %s", duration)
    log.debug("Output path: %s", output_path)

    try:
        (
            ffmpeg.input(video_path, ss=start_time)
            .output(output_path, t=duration, c="copy")
            .global_args("-loglevel", "error")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        # log.error(f"Error during ffmpeg command: {e.stderr}")
        # raise
        raise FFMpegProcessingError(
            "Error during split_video_at_time ffmpeg command", stderr=e.stderr
        )


def split_video(video_path: str, duration: float, output_pattern_path: str):
    """
    Split a video into multiple segments of specified duration.
    Note: This has not been tested, this is just a utility function, for running as a script.

    Args:
    video_path (str): The path to the input video file.
    duration (int): The duration of each segment in seconds.
    output_pattern (str): The output filename pattern with a placeholder for the segment number. ie this/is/a/path/output%01d.mp4

    Raises:
        FFMpegProcessingError: If an error occurs during the FFmpeg command execution.
    """

    log.info("Splitting video...")
    log.debug("Video path: %s", video_path)
    log.debug("Duration: %d", duration)
    log.debug("Output pattern: %s", output_pattern_path)

    try:
        (
            ffmpeg.input(video_path)
            .output(
                output_pattern_path,
                format="segment",
                segment_time=duration,
                c="copy",
                reset_timestamps=1,
                map=0,
            )
            .global_args("-loglevel", "error")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        # log.error(f"Error during ffmpeg command: {e.stderr}")
        # raise
        raise FFMpegProcessingError(
            "Error during split_video ffmpeg command", stderr=e.stderr
        )


def loop_video_to_audio(audio_duration: float, video_path: str, output_path: str):
    """
    Loop a video to match the specified audio duration and save it as a new video file.

    Args:
        audio_duration (float): The duration of the audio in seconds.
        video_path (str): The path to the input video file.
        output_video_path (str): The path to save the output video file.

    Raises:
        FFMpegProcessingError: If an error occurs during the FFmpeg command execution.
    """

    log.info("Looping video to audio duration...")
    log.debug("Audio duration: %s", audio_duration)
    log.debug("Video path: %s", video_path)
    log.debug("Output video path: %s", output_path)

    video_duration = get_video_duration(video_path)
    log.debug("Video duration: %s", video_duration)
    number_of_repeats = math.ceil(audio_duration / video_duration)

    log.info(f"Looping video {number_of_repeats} times.")

    try:
        (
            ffmpeg.input(video_path, stream_loop=number_of_repeats)
            .output(
                output_path,
                vf=f"trim=duration={audio_duration}",
                acodec="copy",
                preset="ultrafast",
            )
            .global_args("-loglevel", "error")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        # log.error(f"Error during ffmpeg command: {e.stderr}")
        # raise
        raise FFMpegProcessingError(
            "Error during loop_video_to_audio ffmpeg command", stderr=e.stderr
        )


def concatenate_audios(audio_path1: str, audio_path2: str, output_path: str):
    """
    Concatenate two audio files using ffmpeg-python.

    Args:
    audio_path1 (str): Path to the first audio file.
    audio_path2 (str): Path to the second audio file.
    output_path (str): Path where the concatenated output should be saved.

    Raises:
        FFMpegProcessingError: If an error occurs during the FFmpeg command execution.
    """

    log.info("Concatenating audio files...")
    log.debug("Audio path 1: %s", audio_path1)
    log.debug("Audio path 2: %s", audio_path2)
    log.debug("Output path: %s", output_path)

    input_str = f"concat:{audio_path1}|{audio_path2}"
    try:
        (
            ffmpeg.input(input_str)
            .output(output_path, codec="copy")
            .global_args("-loglevel", "error")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        log.error(f"Error during ffmpeg command: {e.stderr}")
        raise


def overlay_image_on_video(
    video_path: str, image_path: str, duration: int, output_path: str
):
    """
    Overlay an image on a video

    Args:
    video_path (str): Path to the input video file.
    image_path (str): Path to the image file to overlay.
    duration (int): Duration in seconds for which the image should be visible on the video.
    output_path (str): Path to the output video file.

    Raises:
        FFMpegProcessingError: If an error occurs during the FFmpeg command execution.
    """

    log.info("Overlaying image on video...")
    log.debug("Video path: %s", video_path)
    log.debug("Image path: %s", image_path)
    log.debug("Duration: %s", duration)
    log.debug("Output path: %s", output_path)

    try:
        input_video = ffmpeg.input(video_path)
        input_image = ffmpeg.input(image_path)

        overlay_filter = (
            ffmpeg.filter_(
                [input_video, input_image],
                "overlay",
                x="(W-w)/2",
                y="(H-h)/2",
                enable=f"between(t,0,{duration})",
            )
            .output(output_path, vcodec="libx264", acodec="copy", preset="ultrafast")
            .global_args("-loglevel", "error")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        # log.error(f"Error during ffmpeg command: {e.stderr}")
        # raise
        raise FFMpegProcessingError(
            "Error during overlay_image_on_video ffmpeg command", stderr=e.stderr
        )


def resize_image(image_path: str, target_width: int, output_path: str):
    """
    Resize an image to a specified width, keeping the aspect ratio.

    Args:
    image_path (str): Path to the input image file.
    target_width (int): Target width for the resized image.
    output_path (str): Output path for the new image file.

    Raises:
        FFMpegProcessingError: If an error occurs during the FFmpeg command execution.
    """
    log.info("Resizing image...")

    log.debug("Image path: %s", image_path)
    log.debug("Target width: %s", target_width)
    log.debug("Output path: %s", output_path)

    # TODO validate why we do this (this line comes from my original java implementation, but I don't remember why I did it)
    target_width += 200

    try:
        (
            ffmpeg.input(image_path)
            .filter("scale", target_width, -1)  # -1 in scale maintains the aspect ratio
            .output(output_path)
            .global_args("-loglevel", "error")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        # log.error(f"Error during ffmpeg command: {e.stderr}")
        # raise
        raise FFMpegProcessingError(
            "Error during resize_image ffmpeg command", stderr=e.stderr
        )


def buffer_audio(audio_path: str, pos: str, duration: float, output_path: str):
    """
    Buffer audio by adding silence at the start or end of the audio file.

    Args:
    audio_path (str): Path to the audio file.
    pos (str): Position to add the buffer ('START' or 'END').
    duration (float): Duration of the silence to add in seconds.
    output_path (str): Output path for the new image file.

    Raises:
        FFMpegProcessingError: If an error occurs during the FFmpeg command execution.
    """
    log.info("Buffering audio...")
    log.debug("Audio path: %s", audio_path)
    log.debug("Position: %s", pos)
    log.debug("Duration: %s", duration)
    log.debug("Output path: %s", output_path)

    # Configure FFmpeg command based on the position of buffering
    if pos == "START":
        log.info("Buffering audio at start...")
        filter_complex = f"adelay={duration}s:all=true"
    elif pos == "END":
        log.info("Buffering audio at end...")
        filter_complex = f"apad=pad_dur={duration}s"
    else:
        raise ValueError("Invalid position. Use 'START' or 'END'.")

    try:
        (
            ffmpeg.input(audio_path)
            .output(output_path, af=filter_complex)
            .global_args("-loglevel", "error")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        # log.error(f"Error during ffmpeg command: {e.stderr}")
        # raise
        raise FFMpegProcessingError(
            "Error during buffer_audio ffmpeg command", stderr=e.stderr
        )


def embed_srt_and_audio(video_path, audio_path, srt_path, output_path):
    """
    Embeds subtitles and audio into a video file using FFmpeg.

    Args:
        video_path (str): The path to the input video file.
        audio_path (str): The path to the input audio file.
        srt_path (str): The path to the input subtitle file in SRT format.
        output_path (str): The path to save the output video file.

    Raises:
        FFMpegProcessingError: If an error occurs during the FFmpeg command execution.
    """

    log.info("Embedding subtitles and audio...")
    log.debug("Video path: %s", video_path)
    log.debug("Audio path: %s", audio_path)
    log.debug("SRT path: %s", srt_path)
    log.debug("Output path: %s", output_path)

    subtitles_filter = f"subtitles={srt_path}:force_style='FontName=Mont,FontSize=20,PrimaryColour=&H00ffffff,OutlineColour=&H00000000,BackColour=&H80000000,Bold=1,Italic=0,Alignment=10,Outline=1.5'"
    try:
        (
            ffmpeg.input(video_path)
            .output(
                ffmpeg.input(audio_path),
                output_path,
                vf=subtitles_filter,
                vcodec="libx264",
                acodec="libmp3lame",
                preset="ultrafast",
            )
            .global_args("-loglevel", "error")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        # log.error(f"Error during ffmpeg command: {e.stderr}")
        # raise
        raise FFMpegProcessingError(
            "Error during embed_srt_and_audio ffmpeg command", stderr=e.stderr
        )


def delay_srt(srt_path: str, delay: float, output_path: str):
    """
    Delay an SRT subtitle file by a certain number of seconds using ffmpeg-python.

    Args:
    srt_path (str): Path to the SRT file.
    delay (float): Amount of delay to add in seconds.
    output_path (str): Path where the delayed SRT file will be saved.

    Raises:
        FFMpegProcessingError: If an error occurs during the FFmpeg command execution.
    """
    log.info(f"Delaying srt by {delay} seconds.")
    log.debug("SRT path: %s", srt_path)
    log.debug("Output path: %s", output_path)

    latency = 0.1  # additional latency to add in seconds
    total_delay = delay + latency

    try:
        (
            ffmpeg.input(srt_path, itsoffset=total_delay)
            .output(output_path, codec="copy")
            .global_args("-loglevel", "error")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        # log.error(f"Error during ffmpeg command: {e.stderr}")
        # raise
        raise FFMpegProcessingError(
            "Error during delay_srt ffmpeg command", stderr=e.stderr
        )


def get_video_duration(video_path: str) -> float:
    """Returns the duration of the video in seconds."""

    log.info("Getting video duration...")
    log.debug("Video path: %s", video_path)

    probe = ffmpeg.probe(video_path)
    duration = float(
        next(stream for stream in probe["streams"] if stream["codec_type"] == "video")[
            "duration"
        ]
    )
    return duration


def get_video_dimensions(video_path: str) -> tuple:
    """
    Get the dimensions of a video file.

    Args:
    video_path (str): The path to the video file.

    Returns:
    tuple (width:int, height:int): A tuple containing the width and height of the video.
    """

    log.info("Getting video dimensions...")
    log.debug("Video path: %s", video_path)

    probe = ffmpeg.probe(video_path)
    video_streams = [
        stream for stream in probe["streams"] if stream["codec_type"] == "video"
    ]
    width = int(video_streams[0]["width"])
    height = int(video_streams[0]["height"])
    return width, height


def get_audio_duration(audio_path: str):
    """
    Get the duration of an audio file in seconds.

    Args:
    audio_path (str): The file path to the audio file.

    Returns:
    float: Duration of the audio in seconds.
    """

    log.info("Getting audio length...")
    log.debug("Audio path: %s", audio_path)

    probe = ffmpeg.probe(audio_path)
    audio_streams = [
        stream for stream in probe["streams"] if stream["codec_type"] == "audio"
    ]
    if audio_streams:
        duration = float(audio_streams[0]["duration"])
        return duration


# Some additional logic to compress test files
def compress_video(input_path, output_path):
    """Compress video files to a lower bitrate."""
    try:
        (
            ffmpeg.input(input_path)
            .output(
                output_path,
                vcodec="libx264",
                crf=28,
                preset="fast",
                acodec="aac",
                strict="experimental",
            )
            .global_args("-loglevel", "error")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        # log.error(f"Error during ffmpeg command: {e.stderr}")
        # raise
        raise FFMpegProcessingError(
            "Error during compress_video ffmpeg command", stderr=e.stderr
        )


def compress_directory(directory):
    """Compress all MP4 files in the specified directory."""
    for filename in os.listdir(directory):
        if filename.endswith(".mp4"):
            input_path = os.path.join(directory, filename)
            output_path = os.path.join(directory, f"compressed_{filename}")
            log.info(f"Compressing {input_path} to {output_path}...")
            compress_video(input_path, output_path)


if __name__ == "__main__":
    """
    Provides a command-line interface for the ffmpeg utility functions.
    """
    import sys

    if sys.argv[1] == "resize_video":
        resize_video(sys.argv[2], "cmd_line_output.mp4")
    elif sys.argv[1] == "split_video":
        split_video(
            sys.argv[2], cast(float, sys.argv[3]), "cmd_line_looped_output%01d.mp4"
        )
    elif sys.argv[1] == "loop_video_to_audio":
        audio_duration = get_audio_duration(sys.argv[2])
        loop_video_to_audio(
            cast(float, audio_duration), sys.argv[3], "cmd_line_looped_video.mp4"
        )
    elif sys.argv[1] == "compress":
        compress_directory("./tests/fixtures/unit/utils/ffmpeg")
    else:
        print("Invalid command")
        sys.exit(1)
