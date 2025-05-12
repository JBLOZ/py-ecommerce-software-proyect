import unittest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel
import backend.app.main as main_module
import db import registry_module
from sqlmodel import create_engine as _create_engine
from db import Category
from db import Product


class TestAPICore(unittest.TestCase):
    def setUp(self):
        # Forzar engine SQLite en memoria para tests
        registry_module.create_engine = lambda url, echo=True: _create_engine('sqlite:///:memory:', echo=echo)
        # Reiniciar sesión singleton
        registry_module.DatabaseRegistry._DatabaseRegistry__session = None
        # Crear tablas y datos iniciales
        session = registry_module.DatabaseRegistry.session()
        SQLModel.metadata.create_all(session.get_bind())
        session.add(Category(id=1, name='TestCat'))
        session.add(Category(id=2, name='OtherCat'))
        session.add(Product(id=1, name='Prod1', price=9.99, category_id=1))
        session.commit()
        self.client = TestClient(main_module.app)

    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_get_categories(self):
        response = self.client.get('/categories')
        self.assertEqual(response.status_code, 200)
        expected = {'categories': [ {'id': 1, 'name': 'TestCat'}, {'id': 2, 'name': 'OtherCat'} ]}
        self.assertEqual(response.json(), expected)

    def test_get_products(self):
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)
        expected = {'products': [ {'id': 1, 'name': 'Prod1', 'price': 9.99} ]}
        self.assertEqual(response.json(), expected)

    def test_search_text(self):
        response = self.client.post('/search/text', json={'query': 'TestCat'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('categories', data)
        self.assertIn('products', data)


if __name__ == '__main__':
    unittest.main()