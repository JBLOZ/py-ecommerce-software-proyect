import unittest
from unittest.mock import Mock, MagicMock, patch
import uuid
import io
import os
import sys
from fastapi.testclient import TestClient

# Mockear las dependencias externas antes de importar
sys.modules['redis'] = MagicMock()
sys.modules['celery'] = MagicMock()
sys.modules['kombu'] = MagicMock()
sys.modules['kombu.transport'] = MagicMock()
sys.modules['kombu.transport.redis'] = MagicMock()

# Ahora importamos el módulo a testear
from inference.app.inference_controller import router, get_process_image_task


class TestInferenceController(unittest.TestCase):
    
    def setUp(self):
        """Configurar el cliente de test"""
        from fastapi import FastAPI
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)
    
    def test_health_check(self):
        """Test del endpoint de health check"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
    
    def test_get_process_image_task(self):
        """Test de la función de inyección de dependencia"""
        with patch('inference.app.tasks.process_image_task') as mock_task:
            result = get_process_image_task()
            self.assertEqual(result, mock_task)
    
    @patch('inference.app.inference_controller.uuid.uuid4')
    @patch('inference.app.tasks.process_image_task')
    def test_infer_image_success(self, mock_process_task, mock_uuid):
        """Test del endpoint de inferencia asíncrona exitosa"""
        # Configurar mocks
        mock_task_id = "test-task-id-123"
        mock_uuid.return_value = mock_task_id
        
        mock_celery_task = MagicMock()
        mock_celery_task.id = "celery-task-id-456"
        
        mock_process_task.delay.return_value = mock_celery_task
        
        # Crear archivo de prueba
        test_image_data = b"fake image data"
        files = {"file": ("test.jpg", io.BytesIO(test_image_data), "image/jpeg")}
        
        # Hacer la petición
        response = self.client.post("/infer/image", files=files)
        
        # Verificaciones
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"task_id": "celery-task-id-456"})
        mock_process_task.delay.assert_called_once_with(test_image_data, mock_task_id)
    
    @patch('inference.app.inference_controller.uuid.uuid4')
    @patch('inference.app.tasks.process_image_task')
    def test_infer_image_fallback_task_id(self, mock_process_task, mock_uuid):
        """Test del endpoint cuando el task de Celery no tiene id válido"""
        # Configurar mocks
        mock_task_id = "test-task-id-123"
        mock_uuid.return_value = mock_task_id
        
        # Crear un mock que no tenga atributo 'id' realmente
        class MockTaskWithoutId:
            pass
        
        mock_celery_task = MockTaskWithoutId()
        mock_process_task.delay.return_value = mock_celery_task
        
        # Crear archivo de prueba
        test_image_data = b"fake image data"
        files = {"file": ("test.jpg", io.BytesIO(test_image_data), "image/jpeg")}
        
        # Hacer la petición
        response = self.client.post("/infer/image", files=files)
        
        # Verificaciones - debería usar el task_id de fallback
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"task_id": mock_task_id})
    
    @patch.dict('os.environ', {'SQUEEZENET_MODEL_PATH': '/path/to/model.onnx'})
    @patch('inference.app.models.squeezenet.SqueezeNet')
    def test_infer_image_sync_success(self, mock_squeezenet):
        """Test del endpoint de inferencia síncrona exitosa"""
        # Configurar mock del modelo
        mock_model = MagicMock()
        mock_result = {
            "category": [
                {"label": 285, "confidence": 0.9},
                {"label": 281, "confidence": 0.05},
                {"label": 282, "confidence": 0.03}
            ]
        }
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
        mock_squeezenet.assert_called_once_with('/path/to/model.onnx')
        mock_model.assert_called_once_with(test_image_data)
    
    @patch('inference.app.models.squeezenet.SqueezeNet')
    def test_infer_image_sync_default_model_path(self, mock_squeezenet):
        """Test del endpoint síncrono con path por defecto del modelo"""
        # Configurar mock del modelo
        mock_model = MagicMock()
        mock_result = {"category": []}
        mock_model.return_value = mock_result
        mock_squeezenet.return_value = mock_model
        
        # Crear archivo de prueba
        test_image_data = b"fake image data"
        files = {"file": ("test.jpg", io.BytesIO(test_image_data), "image/jpeg")}
        
        # Hacer la petición
        response = self.client.post("/infer/image/sync", files=files)
        
        # Verificaciones
        self.assertEqual(response.status_code, 200)
        mock_squeezenet.assert_called_once_with('squeezenet.onnx')  # Valor por defecto
    
    @patch('inference.app.models.squeezenet.SqueezeNet')
    def test_infer_image_sync_model_error(self, mock_squeezenet):
        """Test del endpoint síncrono cuando el modelo falla"""
        # Configurar mock para que lance excepción
        mock_squeezenet.side_effect = Exception("Model loading failed")
        
        # Crear archivo de prueba
        test_image_data = b"fake image data"
        files = {"file": ("test.jpg", io.BytesIO(test_image_data), "image/jpeg")}
        
        # Hacer la petición y verificar que se propaga la excepción
        with self.assertRaises(Exception):
            self.client.post("/infer/image/sync", files=files)


if __name__ == '__main__':
    unittest.main()
