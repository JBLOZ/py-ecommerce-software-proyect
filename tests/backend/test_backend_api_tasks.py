import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from main import app
from db import Category, Product
from db import DatabaseRegistry
from services import ResultService


class MockPrediction:
    """Clase para simular las predicciones del modelo."""
    def __init__(self, label, score):
        self.label = label
        self.score = score


class TestAPITasks(unittest.TestCase):
    def setUp(self):
        # Crear motor de base de datos en memoria para pruebas
        self.engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        
        # Parchear el método get_engine para usar nuestro motor de prueba
        self.original_get_engine = DatabaseRegistry._DatabaseRegistry__get_engine
        DatabaseRegistry._DatabaseRegistry__get_engine = MagicMock(return_value=self.engine)
        
        # Reiniciar la sesión singleton
        DatabaseRegistry._DatabaseRegistry__session = None
        
        # Crear tablas y poblar con datos de prueba
        SQLModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        
        # Añadir categorías de prueba
        self.session.add(Category(id=1, name='Camisetas'))
        self.session.add(Category(id=2, name='Teléfonos'))
        self.session.add(Category(id=3, name='Pantalones'))
        
        # Añadir productos de prueba
        self.session.add(Product(id=1, name='Camiseta deportiva', price=19.99, category_id=1))
        self.session.add(Product(id=2, name='Smartphone XY123', price=299.99, category_id=2))
        self.session.add(Product(id=3, name='Pantalones vaqueros', price=49.99, category_id=3))
        self.session.commit()
        
        # Crear cliente de prueba
        self.client = TestClient(app)
        
        # Obtener instancia del servicio de resultados y limpiar todos los resultados
        self.result_service = ResultService()
        self.result_service._result_store = {}  # Limpiar resultados anteriores
        
    def test_task_result_not_found(self):
        """Prueba que se devuelve un 202 cuando una tarea no existe."""
        response = self.client.get('/tasks/nonexistent_task_id/result')
        self.assertEqual(response.status_code, 202)  # Aceptado pero procesando
        self.assertIn('proceso', response.json()['detail'].lower())
    
    @patch.object(ResultService, 'has_result')
    @patch.object(ResultService, 'get_result')
    def test_task_result_with_predictions(self, mock_get_result, mock_has_result):
        """Prueba que se devuelven las predicciones correctamente cuando una tarea existe."""
        # Configurar mocks
        task_id = 'task123'
        mock_has_result.return_value = True
        
        # Simular predicciones con puntuaciones superiores al umbral
        mock_predictions = [
            MockPrediction(label=1, score=0.95),  # Camisetas
            MockPrediction(label=3, score=0.75)   # Pantalones
        ]
        mock_get_result.return_value = mock_predictions
        
        # Realizar solicitud
        response = self.client.get(f'/tasks/{task_id}/result')
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verificar que las categorías son correctas
        self.assertIn('categories', data)
        self.assertIn('Camisetas', data['categories'])
        self.assertIn('Pantalones', data['categories'])
        
        # Verificar que los productos son correctos
        self.assertIn('products', data)
        products = data['products']
        self.assertEqual(len(products), 2)  # Debería haber 2 productos (1 de camisetas, 1 de pantalones)
        
        # Verificar los IDs de los productos
        product_ids = [p['id'] for p in products]
        self.assertIn(1, product_ids)  # ID de la camiseta
        self.assertIn(3, product_ids)  # ID del pantalón
    
    @patch.object(ResultService, 'has_result')
    @patch.object(ResultService, 'get_result')
    def test_task_result_below_threshold(self, mock_get_result, mock_has_result):
        """Prueba que se filtran las predicciones por debajo del umbral de confianza."""
        # Configurar mocks
        task_id = 'task456'
        mock_has_result.return_value = True
        
        # Simular una predicción con puntuación inferior al umbral (0.5)
        mock_predictions = [
            MockPrediction(label=2, score=0.3)  # Teléfonos - por debajo del umbral
        ]
        mock_get_result.return_value = mock_predictions
        
        # Realizar solicitud
        response = self.client.get(f'/tasks/{task_id}/result')
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # No debería haber categorías ni productos (puntaje por debajo del umbral)
        self.assertEqual(data['categories'], [])
        self.assertEqual(data['products'], [])


if __name__ == '__main__':
    unittest.main()
