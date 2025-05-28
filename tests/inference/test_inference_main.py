import unittest
from fastapi import FastAPI
from main import app


class TestInferenceMain(unittest.TestCase):
    def test_app_initialization(self):
        self.assertIsInstance(app, FastAPI)
        self.assertTrue(app.routes)

    def test_app_is_fastapi_instance(self):
        self.assertIsInstance(app, FastAPI)

    def test_router_inclusion(self):
        paths = [r.path for r in app.routes if hasattr(r, "path")]
        for p in ["/health", "/infer/image", "/infer/image/sync"]:
            self.assertTrue(any(p == path for path in paths))

    def test_app_routes_structure(self):
        route_map = {r.path: r for r in app.routes if hasattr(r, "path")}
        self.assertIn("GET", route_map["/health"].methods)
        self.assertIn("POST", route_map["/infer/image"].methods)
        self.assertIn("POST", route_map["/infer/image/sync"].methods)

    def test_app_configuration(self):
        self.assertIsNotNone(app.title)
        self.assertTrue(app.routes)

    def test_app_has_basic_fastapi_structure(self):
        for attr in ("routes", "title", "exception_handlers"):
            self.assertTrue(hasattr(app, attr))