import unittest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
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

if __name__ == "__main__":
    unittest.main()
