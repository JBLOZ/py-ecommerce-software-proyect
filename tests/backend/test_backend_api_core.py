import unittest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from unittest.mock import patch, MagicMock

from main import app
from db import Category, Product
from db import DatabaseRegistry


class TestAPICore(unittest.TestCase):
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
        
        # Agregar datos de prueba
        self.session.add(Category(id=1, name='TestCat'))
        self.session.add(Category(id=2, name='OtherCat'))
        self.session.add(Product(id=1, name='Prod1', price=9.99, category_id=1))
        self.session.commit()
        
        # Crear cliente de prueba
        self.client = TestClient(app)

    def tearDown(self):
        # Restaurar el método original
        if hasattr(self, 'original_get_engine'):
            DatabaseRegistry._DatabaseRegistry__get_engine = self.original_get_engine
        self.session.close()
    
    def test_health(self):
        """Prueba que el endpoint /health devuelve el estado correcto."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_get_categories(self):
        """Prueba que el endpoint /categories devuelve todas las categorías."""
        response = self.client.get('/categories')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('categories', data)
        self.assertEqual(len(data['categories']), 2)
        
        categories = data['categories']
        category_names = [cat['name'] for cat in categories]
        self.assertIn('TestCat', category_names)
        self.assertIn('OtherCat', category_names)
        
        # Verificar estructura de los datos
        for category in categories:
            self.assertIn('id', category)
            self.assertIn('name', category)

    def test_get_products(self):
        """Prueba que el endpoint /products devuelve todos los productos."""
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('products', data)
        self.assertEqual(len(data['products']), 1)
        
        product = data['products'][0]
        self.assertEqual(product['id'], 1)
        self.assertEqual(product['name'], 'Prod1')
        self.assertEqual(product['price'], 9.99)

    def test_search_text_found(self):
        """Prueba que el endpoint /search/text devuelve resultados cuando hay coincidencias."""
        response = self.client.post('/search/text', json={'query': 'TestCat'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('categories', data)
        self.assertIn('products', data)
        self.assertIn('TestCat', data['categories'])
        self.assertEqual(len(data['products']), 1)
        
        product = data['products'][0]
        self.assertEqual(product['id'], 1)
        self.assertEqual(product['name'], 'Prod1')
    
    def test_search_text_not_found(self):
        """Prueba que el endpoint /search/text devuelve listas vacías cuando no hay coincidencias."""
        response = self.client.post('/search/text', json={'query': 'NonexistentCategory'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('categories', data)
        self.assertIn('products', data)
        self.assertEqual(len(data['categories']), 0)
        self.assertEqual(len(data['products']), 0)
    
    def test_search_text_empty_query(self):
        """Prueba que el endpoint /search/text maneja correctamente consultas vacías."""
        response = self.client.post('/search/text', json={'query': ''})
        self.assertEqual(response.status_code, 200)
        
    def test_search_text_missing_query(self):
        """Prueba que el endpoint /search/text maneja correctamente solicitudes sin query."""
        response = self.client.post('/search/text', json={})
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()