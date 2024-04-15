import requests
import os
import json
from typing import cast

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

    def generate_srt(self, aligned_object: dict, output_path: str):
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

        for item in aligned_object["words"]:
            if item["case"] != "success":
                log.debug(f"Error aligning the item: {item}")
                continue

            # Start and end times
            start_time = int(item["start"] * 1000)  # Convert to milliseconds
            end_time = int(item["end"] * 1000)  # Convert to milliseconds

            # Format times as SRT requires
            start_srt = f"{start_time // 3600000:02}:{(start_time % 3600000) // 60000:02}:{(start_time % 60000) // 1000:02},{start_time % 1000:03}"
            end_srt = f"{end_time // 3600000:02}:{(end_time % 3600000) // 60000:02}:{(end_time % 60000) // 1000:02},{end_time % 1000:03}"

            # Adding the text
            srt_content += f"{counter}\n{start_srt} --> {end_srt}\n{item['word']}\n\n"
            counter += 1

        with open(output_path, "w") as f:
            f.write(srt_content)
