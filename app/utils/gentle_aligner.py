import requests
import os

from app.utils.logger import log

from app.utils.file_utils import clean_up_file


class GentleAligner:
    def __init__(self):
        self.baseUrl = os.getenv("GENTLE_ALIGNER_URL")
        pass

    def generate_aligned(self, transcript: str, audio_file_path: str) -> object:
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

        with open(audio_file_path, "rb") as audio_file:
            try:
                response = requests.post(
                    url, data={"transcript": transcript}, files={"audio": audio_file}
                )
                log.debug(response)
                response.raise_for_status()

                return response.text

            except requests.exceptions.HTTPError as e:
                log.error(
                    f"HTTP Error requesting Gentle Aligner Docker Service: {response.status_code} - {e}"
                )
                raise e
            except Exception as e:
                log.error(
                    f"Unexpected error requesting Gentle Aligner Docker Service: {e}"
                )
                raise e
