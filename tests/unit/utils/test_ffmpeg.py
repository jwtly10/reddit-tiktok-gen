import unittest
import os

from app.utils.ffmpeg import (
    resize_video,
    loop_video_to_audio,
    get_video_duration,
    get_audio_duration,
    concatenate_audios,
    buffer_audio,
)


class TestFFmpegUtils(unittest.TestCase):
    def setUp(self):
        # Create directory for test files if it does not exist
        self.test_dir = "tmp/test"
        os.makedirs(self.test_dir, exist_ok=True)

    def test_resize_video(self):
        """Test that a video can be resized to maintain a 16:9 aspect ratio"""
        file_under_test = (
            "tests/fixtures/unit/utils/ffmpeg/test_5_second_uncropped_video.mp4"
        )

        output_file = os.path.join(self.test_dir, "test_resized_video.mp4")

        resize_video(file_under_test, output_file)

        self.assertTrue(os.path.exists(output_file))

        # check the new file is smaller than the original
        print(f"Original file size: {os.path.getsize(file_under_test)/ 1024**2: .2f}MB")
        print(f"Resized file size: {os.path.getsize(output_file)/ 1024**2: .2f}MB")

        self.assertTrue(os.path.getsize(output_file) < os.path.getsize(file_under_test))

    def test_loop_video_to_audio(self):
        """Test that a video can be looped to audio"""

        file_under_test = "tests/fixtures/unit/utils/ffmpeg/test_5_second_video.mp4"

        output_file = os.path.join(self.test_dir, "test_looped_video.mp4")

        loop_video_to_audio(10, file_under_test, output_file)

        self.assertTrue(os.path.exists(output_file))

        original_file_size = os.path.getsize(file_under_test) / 1024**2
        looped_file_size = os.path.getsize(output_file) / 1024**2
        print(f"Original file size: {original_file_size: .2f}MB")
        print(f"Looped file size: {looped_file_size: .2f}MB")

        self.assertEqual(get_video_duration(output_file), 10)

    def test_concatenate_audios(self):
        """Test that two audio files can be concatenated"""
        file1 = "tests/fixtures/unit/utils/ffmpeg/test_5_second_audio.mp3"
        file2 = "tests/fixtures/unit/utils/ffmpeg/test_5_second_audio.mp3"

        output_file = os.path.join(self.test_dir, "test_concatenated_audio.mp3")

        concatenate_audios(file1, file2, output_file)

        self.assertTrue(os.path.exists(output_file))

        duration = get_audio_duration(output_file)
        print(f"Duration of concatenated audio: {duration}")

        self.assertAlmostEqual(duration, 10, delta=0.6)

    # TODO
    def test_overlay_image_on_video(self):
        """Test that an image can be overlayed on a video"""
        pass

    def test_resize_image(self):
        """Test that an image can be resized"""
        pass

    def test_buffer_audio_start(self):
        """Test that audio can be buffered"""

        file_under_test = "tests/fixtures/unit/utils/ffmpeg/test_5_second_audio.mp3"

        output_file = os.path.join(self.test_dir, "test_buffered_audio.mp3")

        buffer_audio(file_under_test, "START", 10, output_file)

        self.assertTrue(os.path.exists(output_file))

        duration = get_audio_duration(output_file)

        self.assertAlmostEqual(duration, 15, delta=0.5)

    def test_buffer_audio_end(self):
        """Test that audio can be buffered"""

        file_under_test = "tests/fixtures/unit/utils/ffmpeg/test_5_second_audio.mp3"

        output_file = os.path.join(self.test_dir, "test_buffered_audio.mp3")

        buffer_audio(file_under_test, "END", 10, output_file)

        self.assertTrue(os.path.exists(output_file))

        duration = get_audio_duration(output_file)

        self.assertAlmostEqual(duration, 15, delta=0.5)

    # TODO
    def test_delay_srt_(self):
        """Test that an srt file can be delayed"""
        pass

    def test_get_video_duration(self):
        """Test that the duration of a video can be retrieved"""

        file_under_test = "tests/fixtures/unit/utils/ffmpeg/test_5_second_video.mp4"

        duration = get_video_duration(file_under_test)

        self.assertAlmostEqual(duration, 5, delta=0.2)

    def test_get_audio_duration(self):
        """Test that the duration of an audio file can be retrieved"""

        file_under_test = "tests/fixtures/unit/utils/ffmpeg/test_5_second_audio.mp3"

        duration = get_audio_duration(file_under_test)

        self.assertAlmostEqual(duration, 5, delta=0.2)

    def tearDown(self):
        """Clean up after tests"""
        for file in os.listdir(self.test_dir):
            if os.path.isfile(os.path.join(self.test_dir, file)):
                os.remove(os.path.join(self.test_dir, file))


if __name__ == "__main__":
    unittest.main()
