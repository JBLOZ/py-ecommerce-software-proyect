import importlib
import os
import unittest
from unittest.mock import MagicMock, patch


class TestInferenceTasks(unittest.TestCase):
    # --------------------------------------------------------------- set-up
    def setUp(self) -> None:
        # 1. Celery “vacío” con decorador amable
        self._celery_patcher = patch("celery.Celery")
        celery_cls = self._celery_patcher.start()
        celery_app = MagicMock()

        def fake_task(*a, **kw):
            bind = kw.get("bind", False)

            # @app.task o @app.task()
            def decorator(func):
                def wrapper(*fargs, **fkw):
                    if bind:
                        return func(None, *fargs, **fkw)
                    return func(*fargs, **fkw)
                return wrapper

            # caso sin paréntesis
            if a and callable(a[0]) and not kw:
                return decorator(a[0])
            return decorator

        celery_app.task.side_effect = fake_task
        celery_cls.return_value = celery_app

        # 2. mocks externos
        self._req_patcher = patch("requests.post", autospec=True)
        self.requests_post = self._req_patcher.start()

        self._sqz_patcher = patch(
            "inference.app.models.squeezenet.SqueezeNet", autospec=True
        )
        self.squeeze_cls = self._sqz_patcher.start()

        # 3. import del módulo bajo test
        self.tasks = importlib.import_module("inference.app.tasks")
        importlib.reload(self.tasks)

    # ------------------------------------------------------------- tear-down
    def tearDown(self) -> None:
        for p in (
            self._celery_patcher,
            self._req_patcher,
            self._sqz_patcher,
        ):
            p.stop()

    # ------------------------------------------------------ propiedades cortas
    @property
    def process_image_task(self):
        return self.tasks.process_image_task

    @property
    def redis_url(self):
        return self.tasks.REDIS_URL

    @property
    def backend_webhook(self):
        return self.tasks.BACKEND_WEBHOOK

    # ---------------------------------------------------------------- tests
    def test_celery_app_configuration(self):
        self.assertTrue(self.redis_url.startswith("redis://"))
        self.assertTrue(self.backend_webhook.startswith("http"))

    def test_environment_variables(self):
        self.assertIsInstance(self.redis_url, str)
        self.assertIsInstance(self.backend_webhook, str)

    def test_custom_environment_variables(self):
        env = {
            "REDIS_URL": "redis://custom:6379/1",
            "BACKEND_WEBHOOK_URL": "http://custom:9000/webhook",
        }
        with patch.dict(os.environ, env, clear=False):
            importlib.reload(self.tasks)
            self.assertEqual(self.tasks.REDIS_URL, env["REDIS_URL"])
            self.assertEqual(self.tasks.BACKEND_WEBHOOK, env["BACKEND_WEBHOOK_URL"])

    def test_process_image_task_basic_execution(self):
        self.squeeze_cls.return_value = MagicMock(return_value={"category": []})
        self.process_image_task(b"img", "id-123")
        self.requests_post.assert_called()

    def test_squeezenet_import_path(self):
        self.squeeze_cls.return_value = MagicMock(return_value={"category": []})
        self.process_image_task(b"img", "id-123")
        self.squeeze_cls.assert_called_once()

    def test_process_image_task_integration(self):
        res = {"category": [{"label": 1, "confidence": 0.99}]}
        self.squeeze_cls.return_value = MagicMock(return_value=res)
        self.process_image_task(b"img", "job-1")
        payload = self.requests_post.call_args.kwargs["json"]
        self.assertEqual(payload["state"], "completed")
        self.assertIn("categories", payload)

    def test_process_image_task_error_handling(self):
        self.squeeze_cls.side_effect = RuntimeError("boom")
        self.process_image_task(b"img", "job-2")
        payload = self.requests_post.call_args.kwargs["json"]
        self.assertEqual(payload["state"], "failed")
        self.assertIn("error", payload)