import unittest
from unittest.mock import patch, MagicMock
import io
import sys
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Mockear las dependencias externas antes de importar
sys.modules['redis'] = MagicMock()
sys.modules['celery'] = MagicMock()
sys.modules['kombu'] = MagicMock()
sys.modules['kombu.transport'] = MagicMock()
sys.modules['kombu.transport.redis'] = MagicMock()

# Ahora importamos el módulo a testear
from inference.app.main import app


class TestInferenceMain(unittest.TestCase):
    
    def setUp(self):
        """Configurar el cliente de test"""
        self.client = TestClient(app)
    
    def test_app_initialization(self):
        """Test de inicialización de la aplicación FastAPI"""
        self.assertIsInstance(app, FastAPI)
        # La aplicación se crea sin configuración específica, por lo que usa los valores por defecto
        self.assertEqual(app.title, "FastAPI")
        # No verificamos descripción y versión ya que no están configuradas
        self.assertIsNotNone(app.routes)  # Verificar que tiene rutas configuradas
    
    def test_app_is_fastapi_instance(self):
        """Test de que app es una instancia de FastAPI"""
        self.assertIsInstance(app, FastAPI)
    
    def test_router_inclusion(self):
        """Test de que el router está incluido correctamente"""
        # Verificar que hay rutas registradas
        routes = [route for route in app.routes]
        self.assertTrue(len(routes) > 0)
        
        # Verificar que se incluyen las rutas del inference_controller
        route_paths = [route.path for route in routes if hasattr(route, 'path')]
        expected_paths = ["/health", "/infer/image", "/infer/image/sync"]
        for expected_path in expected_paths:
            found = any(expected_path in path for path in route_paths)
            self.assertTrue(found, f"Ruta {expected_path} no encontrada en {route_paths}")
    
    def test_health_endpoint_through_main_app(self):
        """Test del endpoint de health a través de la aplicación principal"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
    
    @patch('inference.app.models.squeezenet.SqueezeNet')
    def test_sync_inference_endpoint_through_main_app(self, mock_squeezenet):
        """Test del endpoint de inferencia síncrona a través de la aplicación principal"""
        # Configurar mock del modelo
        mock_model = MagicMock()
        mock_result = {"category": [{"label": 285, "confidence": 0.9}]}
        mock_model.return_value = mock_result
        mock_squeezenet.return_value = mock_model
        
        # Crear archivo de prueba
        test_image_data = b"fake image data"
        files = {"file": ("test.jpg", io.BytesIO(test_image_data), "image/jpeg")}
        
        # Hacer la petición
        response = self.client.post("/infer/image/sync", files=files)
        
        # Verificaciones
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_result)
    
    @patch('inference.app.tasks.process_image_task')
    def test_async_inference_endpoint_through_main_app(self, mock_process_task):
        """Test del endpoint de inferencia asíncrona a través de la aplicación principal"""
        # Configurar mocks - crear un mock task que retorna un ID string
        class MockTaskWithId:
            def __init__(self, task_id):
                self.id = task_id
        
        mock_celery_task = MockTaskWithId("celery-task-id-456")
        mock_process_task.delay.return_value = mock_celery_task
        
        # Crear archivo de prueba
        test_image_data = b"fake image data"
        files = {"file": ("test.jpg", io.BytesIO(test_image_data), "image/jpeg")}
        
        # Hacer la petición
        response = self.client.post("/infer/image", files=files)
        
        # Verificaciones
        self.assertEqual(response.status_code, 200)
        self.assertIn("task_id", response.json())
        self.assertEqual(response.json()["task_id"], "celery-task-id-456")
    
    def test_app_routes_methods(self):
        """Test de métodos HTTP permitidos en las rutas"""
        # Verificar métodos para cada endpoint
        health_route = None
        infer_async_route = None
        infer_sync_route = None
        
        for route in app.routes:
            if hasattr(route, 'path'):
                if route.path == "/health":
                    health_route = route
                elif route.path == "/infer/image":
                    infer_async_route = route
                elif route.path == "/infer/image/sync":
                    infer_sync_route = route
        
        # Verificar que las rutas existen
        self.assertIsNotNone(health_route)
        self.assertIsNotNone(infer_async_route)
        self.assertIsNotNone(infer_sync_route)
        
        # Verificar métodos HTTP
        if hasattr(health_route, 'methods'):
            self.assertIn("GET", health_route.methods)
        
        if hasattr(infer_async_route, 'methods'):
            self.assertIn("POST", infer_async_route.methods)
        
        if hasattr(infer_sync_route, 'methods'):
            self.assertIn("POST", infer_sync_route.methods)
    
    def test_invalid_routes(self):
        """Test de rutas que no existen"""
        # Verificar que rutas inexistentes devuelven 404
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)
        
        response = self.client.post("/invalid")
        self.assertEqual(response.status_code, 404)
    
    def test_wrong_method_on_existing_routes(self):
        """Test de métodos HTTP incorrectos en rutas existentes"""
        # POST en endpoint que solo acepta GET
        response = self.client.post("/health")
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        
        # GET en endpoints que solo aceptan POST
        response = self.client.get("/infer/image")
        self.assertEqual(response.status_code, 405)
        
        response = self.client.get("/infer/image/sync")
        self.assertEqual(response.status_code, 405)


if __name__ == '__main__':
    unittest.main()
