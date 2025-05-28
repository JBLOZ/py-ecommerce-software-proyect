import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from services import ResultService


class TestWebhook(unittest.TestCase):
    def setUp(self):
        # Crear cliente de prueba
        self.client = TestClient(app)
        
        # Obtener instancia del servicio de resultados y limpiar todos los resultados
        self.result_service = ResultService()
        self.result_service._result_store = {}  # Limpiar resultados anteriores
    
    @patch.object(ResultService, 'store_result')
    def test_webhook_task_completed(self, mock_store_result):
        """Prueba que el webhook almacena correctamente los resultados."""
        # Datos de prueba
        payload = {
            "task_id": "test_task_123",
            "state": "completed",
            "categories": [
                {"label": 1, "score": 0.95},
                {"label": 2, "score": 0.85}
            ]
        }
        
        # Realizar solicitud al webhook
        response = self.client.post('/webhook/task_completed', json=payload)
        
        # Verificar que se llamó a store_result con los parámetros correctos
        mock_store_result.assert_called_once()
        args = mock_store_result.call_args[0]
        self.assertEqual(args[0], "test_task_123")  # Verificar task_id
        
        # Verificar respuesta HTTP
        self.assertEqual(response.status_code, 202)  # Aceptado
        self.assertEqual(response.json(), {"status": "received"})
    
    def test_webhook_invalid_payload(self):
        """Prueba que el webhook valida correctamente los datos de entrada."""
        # Payload inválido (falta task_id)
        payload = {
            "state": "completed",
            "categories": [
                {"label": 1, "score": 0.95}
            ]
        }
        
        # Realizar solicitud al webhook
        response = self.client.post('/webhook/task_completed', json=payload)
        
        # Verificar que se devuelve un error
        self.assertEqual(response.status_code, 422)  # Error de validación
    
    def test_webhook_invalid_score(self):
        """Prueba que el webhook valida correctamente los valores de score."""
        # Payload con score inválido (fuera del rango 0-1)
        payload = {
            "task_id": "test_task_456",
            "state": "completed",
            "categories": [
                {"label": 1, "score": 1.5}  # Score inválido
            ]
        }
        
        # Realizar solicitud al webhook
        response = self.client.post('/webhook/task_completed', json=payload)
        
        # Verificar que se devuelve un error
        self.assertEqual(response.status_code, 422)  # Error de validación
    
    @patch.object(ResultService, 'store_result')
    def test_webhook_integration_with_service(self, mock_store_result):
        """Prueba la integración entre el webhook y el servicio de resultados."""
        # Simular que se almacena el resultado
        mock_store_result.return_value = None
        
        # Datos de prueba
        task_id = "integration_test_task"
        payload = {
            "task_id": task_id,
            "state": "completed",
            "categories": [
                {"label": 1, "score": 0.95},
                {"label": 3, "score": 0.75}
            ]
        }
        
        # Realizar solicitud al webhook
        response = self.client.post('/webhook/task_completed', json=payload)
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 202)
        
        # Verificar que se llamó al servicio con los parámetros correctos
        mock_store_result.assert_called_once()
        args = mock_store_result.call_args[0]
        self.assertEqual(args[0], task_id)


if __name__ == '__main__':
    unittest.main()
