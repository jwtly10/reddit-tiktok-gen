import unittest

import app.config

from app.utils.openai import determine_gender_from_text, improve_content_from_text


class TestOpenAI(unittest.TestCase):
    def test_determine_gender_from_text(self):
        text = "I (25F), have a boyfriend who always wakes up at 5am to make me breakfast. Is this normal?"

        res = determine_gender_from_text(text)

        self.assertEqual(res, "f")

    def test_improve_content_from_text(self):
        text = "This is a short story about a high-end store robbery. The store had people break in and steal items."

        res = improve_content_from_text(text)

        self.assertEqual(
            res,
            "This is a short story about a high end store robbery. The store had people break in and steal items.",
        )


if __name__ == "__main__":
    unittest.main()
