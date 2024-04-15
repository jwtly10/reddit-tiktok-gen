import unittest
import os
from unittest.mock import patch, AsyncMock
import app.service.generate as generate
import asyncio


class TestVideoGeneration(unittest.IsolatedAsyncioTestCase):
    @patch("app.service.generate.ElevenLabs")
    @patch("app.service.generate.determine_gender_from_text")
    @patch("app.service.generate.update_job_step", new_callable=AsyncMock)
    @patch("app.service.generate.fail_job", new_callable=AsyncMock)
    async def test_generate_video_from_content(
        self,
        mock_fail_job,
        mock_update_job_step,
        mock_determine_gender,
        mock_elevenlabs,
    ):
        mock_update_job_step.return_value = asyncio.Future()
        mock_update_job_step.return_value.set_result(None)

        mock_fail_job.return_value = asyncio.Future()
        mock_fail_job.return_value.set_result(None)

        mock_determine_gender.return_value = "m"
        mock_elevenlabs_instance = mock_elevenlabs.return_value
        mock_elevenlabs_instance.generate_mp3.return_value = None

        mock_session = AsyncMock()

        test_post = """
        I'll keep it brief because it's so timely. Am I the asshole because it's Father's Day and all I wanted to do was spend time alone in the backyard, smoking a cigar, and listening to music/podcasts by myself? I recognize without kids, I am not a subject of this holiday, but my wife and kids are giving the pass and I'm taking it. Yet part of me still wonders...
        """
        test_title = """
        AITA Short and sweet
        """
        test_id = "tempid"

        test_base_vid_path = os.path.join(
            "base_background_media", "minecraft_background_video_1.mp4"
        )

        output_dir = os.path.join(
            "tests",
            "fixtures",
            "integration",
            "service",
            "generate",
            # , id
        )

        await generate.generate_video_from_content(
            test_id, test_title, test_post, test_base_vid_path, output_dir, mock_session
        )

        expected_final_video_path = os.path.join(output_dir, "final.mp4")

        self.assertTrue(os.path.exists(expected_final_video_path))
        self.assertTrue(os.path.getsize(expected_final_video_path) > 0)


if __name__ == "__main__":
    unittest.main()
