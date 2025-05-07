import pytest
from sqlmodel import create_engine as _create_engine
from backend.app.db.registry import DatabaseRegistry
from backend.app.db.entities.category import Category
from backend.app.db.entities.product import Product

@pytest.fixture(autouse=True)
def setup_sqlite(monkeypatch):
    # Forzar engine SQLite en memoria para tests
    monkeypatch.setattr(
        'backend.app.db.registry.create_engine',
        lambda url, echo=True: _create_engine('sqlite:///:memory:', echo=echo)
    )
    # Reiniciar sesión singleton
    DatabaseRegistry._DatabaseRegistry__session = None
    yield


def test_category_crud():
    session = DatabaseRegistry.session()
    cat = Category(id=1, name='TestCat')
    session.add(cat)
    session.commit()
    retrieved = session.get(Category, 1)
    assert retrieved and retrieved.name == 'TestCat'


def test_product_crud():
    session = DatabaseRegistry.session()
    # Asegurar categoría existente
    cat = Category(id=2, name='Another')
    session.add(cat)
    session.commit()
    prod = Product(id=1, name='Prod1', description=None, price=9.99, category_id=2)
    session.add(prod)
    session.commit()
    retrieved = session.get(Product, 1)
    assert retrieved.name == 'Prod1'
    assert retrieved.category_id == 2