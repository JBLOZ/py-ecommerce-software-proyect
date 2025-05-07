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


def test_multiple_products():
    session = DatabaseRegistry.session()
    # Crear categoría para productos
    cat = Category(id=100, name='MultiCat')
    session.add(cat)
    session.commit()
    # Insertar varios productos
    products = [Product(id=i, name=f'Prod{i}', price=1.0*i, category_id=100) for i in range(1, 4)]
    for p in products:
        session.add(p)
    session.commit()
    from sqlmodel import select
    all_prods = session.exec(select(Product)).all()
    assert len(all_prods) == 3

from sqlalchemy.exc import IntegrityError


def test_product_missing_required_field():
    session = DatabaseRegistry.session()
    # Intentar crear producto sin nombre debe fallar
    prod = Product(id=200, name=None, price=5.0, category_id=None)
    with pytest.raises(Exception):
        session.add(prod)
        session.commit()