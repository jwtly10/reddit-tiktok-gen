import unittest
import os
import json

from app.utils.gentle_aligner import GentleAligner


class TestGentleAligner(unittest.TestCase):
    def setUp(self):
        """Set up test variables and environment"""
        self.test_dir = "tmp/test"
        self.gentle_aligner = GentleAligner()
        self.test_fiture_path = os.path.join(
            "tests/fixtures/unit/utils/gentle_aligner", "test_aligned.txt"
        )
        self.filename = "test_srt.srt"

    def test_generate_srt_from_aligned(self):
        """Test that the aligner can generate SRT file from aligned object"""

        aligned = {}
        with open(self.test_fiture_path, "r") as f:
            aligned = json.load(f)

        print(aligned)

        os.makedirs("tmp/test", exist_ok=True)
        output_file = os.path.join("tmp/test", self.filename)
        self.gentle_aligner.generate_srt(aligned, output_file)

        self.assertTrue(output_file)

        file_size = os.path.getsize(output_file)
        self.assertGreater(file_size, 0, "Generated SRT file is empty.")

    def tearDown(self):
        """Clean up after tests"""
        for file in os.listdir(self.test_dir):
            if os.path.isfile(os.path.join(self.test_dir, file)):
                os.remove(os.path.join(self.test_dir, file))


if __name__ == "__main__":
    unittest.main()
