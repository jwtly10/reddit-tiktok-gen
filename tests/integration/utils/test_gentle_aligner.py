import unittest
import os

import app.config

from app.utils.gentle_aligner import GentleAligner


class TestGentleAligner(unittest.TestCase):
    def setUp(self):
        """Set up test variables and environment"""
        self.transcript = """
        I (34F) am in the process of divorcing my husband (33M). We're on good terms and still live together in my house (the house is in my name and was bought before marriage, which means my husband is not entitled to it according to my countries law). He hasn't moved out yet because of his financial issues (I'm ok with it). He just started a new job and hopes to move out in a month or 2.

My MIL is a nasty person and we never got along. She never liked me and made sure I didn't feel welcome in the family. Last month she called me on my birthday to tell me she's glad she no longer has to buy me anything for my birthday because I'm no longer family (she had recently found out we'd be getting a divorce).

Yesterday she called me (my ex was at work and didn't pick up that's why she called me not him) to inform she'd be coming over for 2 days next week because she will be having a medical procedure done in our city (the capital). She does not drive so she can't go home straight after the procedure, she was planning to spend the night and take a bus the next day. I told her absolutely no, she's no longer family, the house is mine and I don't want random people I don't even like in my house.

Neither she nor my ex can afford a hotel. He can't drive her back because of his new work. I won't because she's no longer my problem. My ex is very angry with me and told me I shouldn't be taking out my frustrations on his mother. I'm not. I just don't want her here because I don't like her and I don't feel like I have to put up with this anymore. We're no longer a couple. AITAH?
"""
        self.audio_file_path = (
            "tests/fixtures/integration/utils/gentle_aligner/test_audio.mp3"
        )
        self.gentle_aligner = GentleAligner()

    def test_generate_srt(self):
        """Test that the SRT file is generated correctly using GentleAligner"""
        gentle_aligner_url = os.getenv("GENTLE_ALIGNER_URL")
        if not gentle_aligner_url:
            self.fail("GENTLE_ALIGNER_URL environment variable not set")

        # Raises exception, failing test if we cannot generate srt
        aligned = self.gentle_aligner.generate_aligned(
            self.transcript, self.audio_file_path
        )

        self.assertIsNotNone(aligned)
        self.assertGreater(len(aligned), 0, "Generated AlignedObject is empty.")


if __name__ == "__main__":
    unittest.main()
