import unittest
import os

import app.config

from app.utils.elevenlabs import ElevenLabs


class TestElevenLabs(unittest.TestCase):
    def setUp(self):
        """Set up test variables and environment"""
        self.text = "Hello, this is a test."
        self.gender = "m"
        self.output_path = "tmp/test/test_elevenlabs.mp3"
        self.test_dir = "tmp/test"
        self.eleven_labs = ElevenLabs()

    def test_generate_mp3(self):
        """Test that the MP3 file is generated correctly using ElevenLabs"""
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            self.fail("ELEVENLABS_API_KEY environment variable not set")

        os.makedirs(self.test_dir, exist_ok=True)
        # Raises execption, failing test we cannot generate mp3
        self.eleven_labs.generate_mp3(self.text, self.gender, self.output_path)

        self.assertTrue(os.path.exists(self.output_path))

        file_size = os.path.getsize(self.output_path)
        self.assertGreater(file_size, 0, "Generated file is empty.")

    def tearDown(self):
        """Clean up after tests"""
        # Remove generated file to clean up the directory
        if os.path.exists(self.output_path):
            os.remove(self.output_path)


if __name__ == "__main__":
    unittest.main()
