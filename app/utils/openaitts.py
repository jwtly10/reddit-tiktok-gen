import os

from app.utils.tts import TTS
from app.utils.logger import log

from app.utils.openaitts_voice_id import OpenAiTTSVoiceId

from openai import OpenAI


class OpenAITTS(TTS):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        pass

    def generate_mp3(self, text: str, gender: str, output_path: str):
        voiceid = OpenAiTTSVoiceId.FEMALE if gender == "f" else OpenAiTTSVoiceId.MALE

        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voiceid,
                input=text,
            )
            response.write_to_file(output_path)
        except Exception as e:
            log.error(f"An error occurred generating MP3 file with OpenAI: {e}")
            raise
