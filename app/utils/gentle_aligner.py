import requests
import os
import json
from typing import cast
import re

from app.utils.logger import log


class GentleAligner:
    def __init__(self):
        self.baseUrl = cast(str, os.getenv("GENTLE_ALIGNER_URL"))
        pass

    def generate_aligned(self, transcript: str, audio_file_path: str) -> dict:
        """
        Generates aligned content by sending a transcript and audio file to the Gentle Aligner Docker Service.

        Args:
            transcript (str): The transcript to be aligned.
            audio_file_path (str): The path to the audio file.

        Returns:
            object: The response text from the Gentle Aligner Docker Service.

        Raises:
            requests.exceptions.HTTPError: If there is an HTTP error while requesting the Gentle Aligner Docker Service.
            Exception: If there is an unexpected error while requesting the Gentle Aligner Docker Service.
        """

        log.info("Aligning content")
        url = os.path.join(self.baseUrl, "transcriptions?async=false")

        transcript = self.clean_up_transcript(transcript)

        response = None
        with open(audio_file_path, "rb") as audio_file:
            try:
                response = requests.post(
                    url, data={"transcript": transcript}, files={"audio": audio_file}
                )
                log.debug(f"Aligner res: {response}")
                response.raise_for_status()

                return response.text

            except requests.exceptions.HTTPError as e:
                if response is not None:
                    log.error(
                        f"HTTP Error requesting Gentle Aligner Docker Service: {response.status_code} - {e}"
                    )

                raise e
            except Exception as e:
                log.error(
                    f"Unexpected error requesting Gentle Aligner Docker Service: {e}"
                )
                raise e

    def generate_srt(self, aligned_object: str, output_path: str):
        """
        Generate an SRT file from the aligned object.

        Args:
            aligned_object (dict): The aligned object containing the words and their timings.
            output_path (str): The path to save the SRT file.

        Returns:
            None
        """

        srt_content = ""
        counter = 1

        # log.debug(f"Aligned object: {aligned_object}")

        aligned_object = json.loads(aligned_object)
        log.debug(
            f"Type of aligned_object (should be json/dict): {type(aligned_object)}"
        )

        counter = 1
        srt_content = ""
        group_size = 3
        temp_words = []
        temp_start = None
        temp_end = None

        len_of_aligned_object = len(aligned_object["words"])

        # TODO: Clean up this code
        for i in range(0, len_of_aligned_object, 1):
            if aligned_object["words"][i]["case"] != "success":
                log.debug(f"Error aligning the item: {aligned_object['words'][i]}")
                continue

            # Set the start time of the group
            if not temp_start:
                temp_start = aligned_object["words"][i]["start"]

            # Update the end time to the last word's end time in the group
            temp_end = aligned_object["words"][i]["end"]
            temp_words.append(aligned_object["words"][i]["word"])

            # If it's the last word, write the group
            if i == len_of_aligned_object - 1:
                start_time = int(temp_start * 1000)
                end_time = int(temp_end * 1000)

                start_srt = f"{start_time // 3600000:02}:{(start_time % 3600000) // 60000:02}:{(start_time % 60000) // 1000:02},{start_time % 1000:03}"
                end_srt = f"{end_time // 3600000:02}:{(end_time % 3600000) // 60000:02}:{(end_time % 60000) // 1000:02},{end_time % 1000:03}"

                words_str = " ".join(temp_words)
                srt_content += f"{counter}\n{start_srt} --> {end_srt}\n{words_str}\n\n"
                continue

            # if the next word is capitalized, write the group, but only if the current word is not capitalized
            if (
                i + 1 < len_of_aligned_object
                and aligned_object["words"][i + 1]["word"][0].isupper()
                and aligned_object["words"][i]["word"][0].islower()
            ):
                start_time = int(temp_start * 1000)
                end_time = int(temp_end * 1000)

                start_srt = f"{start_time // 3600000:02}:{(start_time % 3600000) // 60000:02}:{(start_time % 60000) // 1000:02},{start_time % 1000:03}"
                end_srt = f"{end_time // 3600000:02}:{(end_time % 3600000) // 60000:02}:{(end_time % 60000) // 1000:02},{end_time % 1000:03}"

                words_str = " ".join(temp_words)
                srt_content += f"{counter}\n{start_srt} --> {end_srt}\n{words_str}\n\n"
                counter += 1

                temp_words = []
                temp_start = None
                temp_end = None
                continue

            if len(temp_words) == group_size:
                start_time = int(temp_start * 1000)
                end_time = int(temp_end * 1000)

                start_srt = f"{start_time // 3600000:02}:{(start_time % 3600000) // 60000:02}:{(start_time % 60000) // 1000:02},{start_time % 1000:03}"
                end_srt = f"{end_time // 3600000:02}:{(end_time % 3600000) // 60000:02}:{(end_time % 60000) // 1000:02},{end_time % 1000:03}"

                words_str = " ".join(temp_words)
                srt_content += f"{counter}\n{start_srt} --> {end_srt}\n{words_str}\n\n"
                counter += 1

                temp_words = []
                temp_start = None
                temp_end = None

        # Handle any remaining words that didn't make a full group
        if temp_words:
            start_time = int(cast(int, temp_start) * 1000)
            end_time = int(cast(int, temp_end) * 1000)

            start_srt = f"{start_time // 3600000:02}:{(start_time % 3600000) // 60000:02}:{(start_time % 60000) // 1000:02},{start_time % 1000:03}"
            end_srt = f"{end_time // 3600000:02}:{(end_time % 3600000) // 60000:02}:{(end_time % 60000) // 1000:02},{end_time % 1000:03}"

            words_str = " ".join(temp_words)
            srt_content += f"{counter}\n{start_srt} --> {end_srt}\n{words_str}\n\n"

        try:
            with open(output_path, "w") as f:
                f.write(srt_content)
        except Exception as e:
            log.error(f"Error writing SRT file: {e}")
            raise e

    def clean_up_transcript(self, transcript: str) -> str:
        """
        Cleans up the transcript for better alignment accuracy.

        Args:
            transcript (str): The transcript to be cleaned up.

        Returns:
            str: The cleaned up transcript.
        """

        pattern = r"\b(\w+)-(\w+)\b"
        result = re.sub(pattern, r"\1 \2", transcript)

        result = result.replace(":", " ")

        return result
