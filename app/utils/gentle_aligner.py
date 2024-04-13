import requests
import os

from app.utils.logger import log

from app.utils.file_utils import clean_up_file


class GentleAligner:
    def __init__(self):
        self.baseUrl = os.getenv("GENTLE_ALIGNER_URL")
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

    def generate_srt(self, aligned_object: dict, file_name: str):
        """
        Generate an SRT file from the aligned object.

        Args:
            aligned_object (dict): The aligned object containing the words and their timings.
            file_name (str): The name of the SRT file to be generated.

        Returns:
            None
        """

        srt_path = os.path.join("tmp/srt", f"{file_name}.srt")

        srt_content = ""
        counter = 1

        log.debug(f"Aligned object: {aligned_object}")

        for item in aligned_object["words"]:
            if item["case"] != "success":
                print(f"Error aligning the item: {item}")
                continue

            print(f"Item: {item}")
            # Start and end times
            start_time = int(item["start"] * 1000)  # Convert to milliseconds
            end_time = int(item["end"] * 1000)  # Convert to milliseconds

            # Format times as SRT requires
            start_srt = f"{start_time // 3600000:02}:{(start_time % 3600000) // 60000:02}:{(start_time % 60000) // 1000:02},{start_time % 1000:03}"
            end_srt = f"{end_time // 3600000:02}:{(end_time % 3600000) // 60000:02}:{(end_time % 60000) // 1000:02},{end_time % 1000:03}"

            # Adding the text
            srt_content += f"{counter}\n{start_srt} --> {end_srt}\n{item['word']}\n\n"
            counter += 1

        with open(srt_path, "w") as f:
            f.write(srt_content)
