import unittest
import os

from app.utils.image_generator import generate_title_image


class TestTitleImageGenerator(unittest.TestCase):
    def setUp(self):
        # Create directory for test files if it does not exist
        self.test_dir = "tmp/test"
        os.makedirs(self.test_dir, exist_ok=True)

    def test_generate_title_image(self):
        """Test that a title can be generated"""
        test_template = (
            "tests/fixtures/unit/utils/image_generator/reddit_title_template.png"
        )

        output_file = os.path.join(self.test_dir, "title_image.png")

        title = "This is a very long title that needs to be wrapped because it exceeds the maximum img width."

        generate_title_image(output_file, title)

        self.assertTrue(os.path.exists(output_file))

        print(f"Original template size: {os.path.getsize(test_template)}")
        print(f"Generated image size: {os.path.getsize(output_file)}")

        # Check that the generated image is larger than the template
        self.assertTrue(os.path.getsize(output_file) > os.path.getsize(test_template))

    def test_max_title_length(self):
        """Test that a ValueError is raised if the title is too long"""
        title = "This is a very long title that will throw an error if its used for the title of a post. The reason is there is only so much space available for the title."

        with self.assertRaises(ValueError):
            generate_title_image("tmp/test/output_path.png", title)

    def tearDown(self):
        """Clean up after tests"""
        for file in os.listdir(self.test_dir):
            if os.path.isfile(os.path.join(self.test_dir, file)):
                os.remove(os.path.join(self.test_dir, file))


if __name__ == "__main__":
    unittest.main()
