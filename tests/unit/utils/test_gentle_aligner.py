import unittest
import os
import json

from app.utils.gentle_aligner import GentleAligner


class TestGentleAligner(unittest.TestCase):
    def setUp(self):
        """Set up test variables and environment"""
        self.gentle_aligner = GentleAligner()
        self.test_fiture_path = os.path.join(
            "tests/fixtures/unit/utils/gentle_aligner", "test_aligned.txt"
        )

    def test_generate_srt_from_aligned(self):
        """Test that the aligner can generate SRT file from aligned object"""

        aligned = {}
        with open(self.test_fiture_path, "r") as f:
            aligned = json.load(f)

        print(aligned)

        file_name = "test_srt"
        self.gentle_aligner.generate_srt(aligned, file_name)

        srt_path = os.path.join("tmp/srt", f"{file_name}.srt")
        self.assertTrue(os.path.exists(srt_path))

        file_size = os.path.getsize(srt_path)
        self.assertGreater(file_size, 0, "Generated SRT file is empty.")

    # def tearDown(self):
    #     """Clean up after tests"""
    #     # Remove generated file to clean up the directory
    #     file_path = os.path.join("tmp/srt", f"{self.filename}.srt")
    #     if os.path.exists(file_path):
    #         os.remove(file_path)


if __name__ == "__main__":
    unittest.main()
