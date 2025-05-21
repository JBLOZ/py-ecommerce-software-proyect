import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from inference_controller import get_process_image_task

class TestInferenceController(unittest.TestCase):
    def setUp(self):
        # Mock de la task y su método delay para evitar conexión real a Celery/Redis
        mock_task = MagicMock()
        mock_delay_result = MagicMock()
        mock_delay_result.id = "fake-task-id"
        mock_task.delay.return_value = mock_delay_result
        app.dependency_overrides[get_process_image_task] = lambda: mock_task
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_infer_image(self):
        file_content = b"fake image data"
        response = self.client.post(
            "/infer/image",
            files={"file": ("test.jpg", file_content, "image/jpeg")}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("task_id", response.json())
        self.assertEqual(response.json()["task_id"], "fake-task-id")

    @patch("models.SqueezeNet")
    def test_infer_image_sync(self, mock_squeezenet):
        mock_model = MagicMock()
        mock_model.return_value = [
            {"label": 1, "confidence": 0.95},
            {"label": 3, "confidence": 0.83},
            {"label": 5, "confidence": 0.78}
        ]
        mock_squeezenet.return_value = mock_model
        file_content = b"fake image data"
        response = self.client.post(
            "/infer/image/sync",
            files={"file": ("test.jpg", file_content, "image/jpeg")}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("category", response.json())
        self.assertIsInstance(response.json()["category"], list)
        self.assertIn("label", response.json()["category"][0])
        self.assertIn("confidence", response.json()["category"][0])

if __name__ == "__main__":
    unittest.main()
