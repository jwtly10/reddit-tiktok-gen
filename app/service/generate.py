import os

from sqlalchemy.ext.asyncio import AsyncSession


from app.utils.elevenlabs import ElevenLabs
from app.utils.image_generator import generate_title_image
from app.utils.gentle_aligner import GentleAligner
from app.utils.openai import determine_gender_from_text
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

from app.repository.job_repository import update_job_step, fail_job

import app.config

from app.utils.logger import log


async def generate_video_from_content(
    id: int,
    title: str,
    content: str,
    base_background_video: str,
    output_dir: str,
    db: AsyncSession,
):
    """
    Generate a video from the given content.

    Args:
        id (int): The ID of the video.
        title (str): The title of the video.
        content (str): The content of the video.
        base_background_video (str): The path to the base background video.
        output_dir (str): The directory where the generated media will be saved.

    Raises:
        FFMpegProcessingError: If an error occurs during video processing using ffmpeg.
        Exception: If an unexpected error occurs.

    Returns:
        None
    """
    try:
        log.info("Generating video from content")
        log.debug(f"ID: {id}")
        log.debug(f"Title: {title}")
        log.debug(f"Content: {content}")
        log.debug(f"Base Background Video: {base_background_video}")
        log.debug(f"Output Directory: {output_dir}")

        os.makedirs(output_dir, exist_ok=True)

        # Generating audio
        await update_job_step(db, id, "generating_audio")
        gender = determine_gender_from_text(content)

        elevenlabs = ElevenLabs()
        pre_content_audio = os.path.join(output_dir, "pre_content.mp3")
        elevenlabs.generate_mp3(content, gender, pre_content_audio)

        content_audio = os.path.join(output_dir, "content.mp3")
        buffer_audio(pre_content_audio, "END", 1, content_audio)

        pre_title_audio = os.path.join(output_dir, "pre_title.mp3")
        elevenlabs.generate_mp3(title, gender, pre_title_audio)
        pre_title_audio_duration = get_audio_duration(pre_title_audio)

        title_audio = os.path.join(output_dir, "title.mp3")
        buffer_audio(pre_title_audio, "END", 1, title_audio)
        title_audio_duration = get_audio_duration(title_audio)

        # Generating SRT
        await update_job_step(db, id, "generating_srt")
        gentle_aligner = GentleAligner()
        aligned_text = gentle_aligner.generate_aligned(content, content_audio)

        srt_file = os.path.join(output_dir, "content.srt")
        gentle_aligner.generate_srt(aligned_text, srt_file)

        # Generating Title image
        await update_job_step(db, id, "generating_title_image")
        title_image = os.path.join(output_dir, "title_image.png")
        generate_title_image(title_image, title)

        # Generating background video
        await update_job_step(db, id, "generating_background_video")
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

        # Generating final video
        await update_job_step(db, id, "generating_final_video")
        delayed_srt_file = os.path.join(output_dir, "delayed_content.srt")
        delay_srt(srt_file, title_audio_duration, delayed_srt_file)

        final_video = os.path.join(output_dir, "final.mp4")
        embed_srt_and_audio(overlayed_video, video_audio, delayed_srt_file, final_video)

        log.info(f"Final video generated at {final_video}")
        await update_job_step(db, id, "completed", final_video)

    except FFMpegProcessingError as e:
        log.error(f"{e}: {e.stderr}")
        await fail_job(db, id, str(e))
        raise
    except Exception as e:
        log.error(f"An unexpected error occurred while generating video: {e}")
        await fail_job(db, id, str(e))
        raise
