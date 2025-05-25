import io
import unittest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from main import app
from inference_controller import get_process_image_task
import tasks


class TestInferenceController(unittest.TestCase):
    # -------------------------------------------------------------- set-up
    def setUp(self) -> None:
        # 1. mocks de utilidades
        self.uuid_patcher = patch("uuid.uuid4", autospec=True)
        self.mock_uuid = self.uuid_patcher.start()

        self.sqz_patcher = patch(
            "inference.app.models.squeezenet.SqueezeNet", autospec=True
        )
        self.mock_squeezenet = self.sqz_patcher.start()

        # 2. mock de la Celery-task inyectada por dependencia
        self.mock_celery_task = MagicMock()
        app.dependency_overrides[get_process_image_task] = (
            lambda: self.mock_celery_task
        )
        # alias usado por los tests “fallback”
        self.mock_process_task = self.mock_celery_task

        # 3. TestClient sin arrancar lifespan real
        app.lifespan = AsyncMock(return_value=None)
        self.client = TestClient(app)

    # -------------------------------------------------------------- tear-down
    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        self.uuid_patcher.stop()
        self.sqz_patcher.stop()

    # ---------------------------------------------------------------- tests
    def test_health_check(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "ok"})

    def test_get_process_image_task(self):
        with patch.object(tasks, "process_image_task") as mocked:
            self.assertIs(get_process_image_task(), mocked)

    def test_infer_image_success(self):
        self.mock_uuid.return_value = "uuid-123"
        job = MagicMock(id="celery-456")
        self.mock_celery_task.delay.return_value = job

        files = {"file": ("img.jpg", io.BytesIO(b"data"), "image/jpeg")}
        resp = self.client.post("/infer/image", files=files)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"task_id": job.id})
        self.mock_celery_task.delay.assert_called_once()

    def test_infer_image_fallback_task_id(self):
        self.mock_uuid.return_value = "task-id-123"

        class _TaskObj:  # no tiene atributo .id
            pass

        self.mock_process_task.delay.return_value = _TaskObj()

        files = {"file": ("x.jpg", io.BytesIO(b"data"), "image/jpeg")}
        resp = self.client.post("/infer/image", files=files)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"task_id": "task-id-123"})

    def test_infer_image_sync_model_error(self):
        self.mock_squeezenet.side_effect = Exception("boom")

        files = {"file": ("x.jpg", io.BytesIO(b"data"), "image/jpeg")}
        with self.assertRaises(Exception):
            self.client.post("/infer/image/sync", files=files)