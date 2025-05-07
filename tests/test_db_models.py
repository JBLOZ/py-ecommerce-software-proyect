import unittest
from sqlmodel import create_engine as _create_engine, select
import backend.app.db.registry as registry_module
from backend.app.db.entities.category import Category
from backend.app.db.entities.product import Product


class TestDBModels(unittest.TestCase):
    def setUp(self):
        # Patch create_engine para usar sqlite en memoria
        registry_module.create_engine = lambda url, echo=True: _create_engine('sqlite:///:memory:', echo=echo)
        # Reiniciar sesión singleton
        registry_module.DatabaseRegistry._DatabaseRegistry__session = None

    def test_category_crud(self):
        session = registry_module.DatabaseRegistry.session()
        cat = Category(id=1, name='TestCat')
        session.add(cat)
        session.commit()
        retrieved = session.get(Category, 1)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, 'TestCat')

    def test_product_crud(self):
        session = registry_module.DatabaseRegistry.session()
        cat = Category(id=2, name='Another')
        session.add(cat)
        session.commit()
        prod = Product(id=1, name='Prod1', description=None, price=9.99, category_id=2)
        session.add(prod)
        session.commit()
        retrieved = session.get(Product, 1)
        self.assertEqual(retrieved.name, 'Prod1')
        self.assertEqual(retrieved.category_id, 2)

    def test_multiple_products(self):
        session = registry_module.DatabaseRegistry.session()
        cat = Category(id=100, name='MultiCat')
        session.add(cat)
        session.commit()
        products = [Product(id=i, name=f'Prod{i}', price=1.0*i, category_id=100) for i in range(1, 4)]
        for p in products:
            session.add(p)
        session.commit()
        all_prods = session.exec(select(Product)).all()
        self.assertEqual(len(all_prods), 3)

    def test_product_missing_required_field(self):
        session = registry_module.DatabaseRegistry.session()
        prod = Product(id=200, name=None, price=5.0, category_id=None)
        with self.assertRaises(Exception):
            session.add(prod)
            session.commit()


if __name__ == '__main__':
    unittest.main()