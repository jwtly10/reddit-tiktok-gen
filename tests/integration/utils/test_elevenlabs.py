import unittest
import os

import app.config

from app.utils.elevenlabs import ElevenLabs


class TestElevenLabs(unittest.TestCase):
    def setUp(self):
        """Set up test variables and environment"""
        self.text = "Hello, this is a test."
        self.gender = "m"
        self.filename = "test_audio"
        self.eleven_labs = ElevenLabs()

    def test_generate_mp3(self):
        """Test that the MP3 file is generated correctly using ElevenLabs"""
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            self.fail("ELEVENLABS_API_KEY environment variable not set")

        self.eleven_labs.generate_mp3(self.text, self.gender, self.filename)

        audio_directory = "tmp/audio"
        file_path = os.path.join(audio_directory, f"{self.filename}.mp3")
        self.assertTrue(os.path.exists(file_path))

        file_size = os.path.getsize(file_path)
        self.assertGreater(file_size, 0, "Generated file is empty.")

    def tearDown(self):
        """Clean up after tests"""
        # Remove generated file to clean up the directory
        file_path = os.path.join("tmp/audio", f"{self.filename}.mp3")
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == "__main__":
    unittest.main()
