import unittest
from sqlmodel import create_engine as _create_engine, select, SQLModel, Session
from sqlmodel.pool import StaticPool
from unittest.mock import patch, MagicMock

from db import DatabaseRegistry, Category, Product


class TestDBModels(unittest.TestCase):
    def setUp(self):
        # Crear motor de base de datos en memoria para pruebas
        self.engine = _create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        
        # Parchear el método get_engine para usar nuestro motor de prueba
        self.original_get_engine = DatabaseRegistry._DatabaseRegistry__get_engine
        DatabaseRegistry._DatabaseRegistry__get_engine = MagicMock(return_value=self.engine)
        
        # Reiniciar la sesión singleton
        DatabaseRegistry._DatabaseRegistry__session = None
        
        # Crear tablas
        SQLModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)

    def tearDown(self):
        # Restaurar el método original
        if hasattr(self, 'original_get_engine'):
            DatabaseRegistry._DatabaseRegistry__get_engine = self.original_get_engine
        self.session.close()
        
    def test_category_crud(self):
        cat = Category(id=1, name='TestCat')
        self.session.add(cat)
        self.session.commit()
        retrieved = self.session.get(Category, 1)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, 'TestCat')

    def test_product_crud(self):
        cat = Category(id=2, name='Another')
        self.session.add(cat)
        self.session.commit()
        prod = Product(id=1, name='Prod1', description=None, price=9.99, category_id=2)
        self.session.add(prod)
        self.session.commit()
        retrieved = self.session.get(Product, 1)
        self.assertEqual(retrieved.name, 'Prod1')
        self.assertEqual(retrieved.category_id, 2)

    def test_multiple_products(self):
        cat = Category(id=100, name='MultiCat')
        self.session.add(cat)
        self.session.commit()
        products = [Product(id=i, name=f'Prod{i}', price=1.0*i, category_id=100) for i in range(1, 4)]
        for p in products:
            self.session.add(p)
        self.session.commit()
        all_prods = self.session.exec(select(Product)).all()
        self.assertEqual(len(all_prods), 3)

    def test_product_missing_required_field(self):
        prod = Product(id=200, name=None, price=5.0, category_id=None)
        with self.assertRaises(Exception):
            self.session.add(prod)
            self.session.commit()


if __name__ == '__main__':
    unittest.main()