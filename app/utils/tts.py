from abc import ABC, abstractmethod


class TTS(ABC):
    @abstractmethod
    def generate_mp3(self, text: str, gender: str, output_path: str):
        """
        Generates an MP3 file from the given text using the specified gender voice.

        Args:
            text (str): The text to convert to speech.
            gender (str): The gender of the voice to use for the speech generation.
            output_path (str): The path to save the generated MP3 file.

        Returns:
            None
        """
        pass
