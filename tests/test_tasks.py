import unittest
from unittest.mock import patch, MagicMock
from tasks import process_image_task


class TestProcessImageTask(unittest.TestCase):
    @patch("models.SqueezeNet")
    @patch("tasks.requests.post")
    def test_process_image_task_success(self, mock_post, mock_squeezenet):
        mock_model = MagicMock()
        mock_model.return_value = [
            {"label": 1, "confidence": 0.95},
            {"label": 3, "confidence": 0.83},
            {"label": 5, "confidence": 0.78}
        ]
        mock_squeezenet.return_value = mock_model
        image_data = b"fake image"
        task_id = "123"
        process_image_task(image_data, task_id)
        mock_post.assert_called()
        args, kwargs = mock_post.call_args
        self.assertIn("completed", kwargs["json"].values())
        self.assertIn("category", kwargs["json"])  # predictions
        self.assertIsInstance(kwargs["json"]["category"], list)
        self.assertIn("label", kwargs["json"]["category"][0])
        self.assertIn("confidence", kwargs["json"]["category"][0])

    @patch("models.SqueezeNet", side_effect=Exception("fail"))
    @patch("tasks.requests.post")
    def test_process_image_task_failure(self, mock_post, mock_squeezenet):
        image_data = b"fake image"
        task_id = "123"
        process_image_task(image_data, task_id)
        mock_post.assert_called()
        args, kwargs = mock_post.call_args
        self.assertIn("failed", kwargs["json"].values())
        self.assertIn("error", kwargs["json"])  # error message


if __name__ == "__main__":
    unittest.main()
