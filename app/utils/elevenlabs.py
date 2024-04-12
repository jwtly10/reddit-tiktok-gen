import requests
import os

from app.utils.tts import TTS
from app.utils.elevenlabs_voice_id import ElevenLabsVoiceId
from app.utils.logger import log


class ElevenLabs(TTS):
    def __init__(self):
        pass

    def generate_mp3(self, text: str, gender: str, output_filename: str):
        audio_directory = "tmp/audio"
        voiceid = (
            ElevenLabsVoiceId.SOFT_FEMALE
            if gender == "f"
            else ElevenLabsVoiceId.DEEP_MALE
        )

        CHUNK_SIZE = 1024
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voiceid}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
        }

        # todo review model and settings
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
        }

        # create audio directory if it doesnt already exist
        os.makedirs(audio_directory, exist_ok=True)

        file_path = os.path.join(audio_directory, f"{output_filename}.mp3")
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            log.error(f"HTTP Error requesting ElevenLabs: {response.status_code} - {e}")
            raise e
        except Exception as e:
            log.error(f"Unexpected error requests ElevenLabs: {e}")
            raise e

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
