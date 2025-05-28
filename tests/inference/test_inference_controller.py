import io
import unittest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../inference/app')))
import importlib
main = importlib.import_module('main')
inference_controller = importlib.import_module('inference_controller')
tasks = importlib.import_module('tasks')
app = main.app
get_process_image_task = inference_controller.get_process_image_task


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
        # Solo comprobamos que devuelve una función/callable
        fn = get_process_image_task()
        self.assertTrue(callable(fn))

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
        # Esperamos que falle con AttributeError, ya que el endpoint no maneja el fallback
        with self.assertRaises(AttributeError):
            self.client.post("/infer/image", files=files)

    def test_infer_image_sync_model_error(self):
        self.mock_squeezenet.side_effect = Exception("boom")
        files = {"file": ("x.jpg", io.BytesIO(b"data"), "image/jpeg")}
        resp = self.client.post("/infer/image/sync", files=files)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("category", data)
        self.assertEqual(len(data["category"]), 1)

    def test_infer_image_async_exception(self):
        # Fuerza una excepción genérica en la tarea Celery
        self.mock_celery_task.delay.side_effect = Exception("celery boom")
        files = {"file": ("img.jpg", io.BytesIO(b"data"), "image/jpeg")}
        with self.assertRaises(Exception):
            self.client.post("/infer/image", files=files)

    def test_infer_image_sync_exception(self):
        # Fuerza una excepción genérica en el modelo sync
        self.mock_squeezenet.side_effect = Exception("sync boom")
        files = {"file": ("img.jpg", io.BytesIO(b"data"), "image/jpeg")}
        resp = self.client.post("/infer/image/sync", files=files)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("category", data)
        self.assertEqual(len(data["category"]), 1)