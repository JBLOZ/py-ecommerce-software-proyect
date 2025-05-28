import sys
import os
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/app')))
import importlib
main = importlib.import_module('main')
from fastapi.testclient import TestClient

client = TestClient(main.app)

@patch('db.DatabaseRegistry.session')
def test_get_categories_real(mock_session):
    mock_session.return_value.exec.return_value.all.return_value = [MagicMock(id=1, name='Camisetas')]
    response = client.get("/categories")
    assert response.status_code == 200
    assert "categories" in response.json()

@patch('db.DatabaseRegistry.session')
def test_get_products_real(mock_session):
    mock_session.return_value.exec.return_value.all.return_value = [MagicMock(id=1, name='Camiseta azul', price=10.0)]
    response = client.get("/products")
    assert response.status_code == 200
    assert "products" in response.json()

def test_health_real():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch('db.DatabaseRegistry.session')
def test_search_text_empty(mock_session):
    mock_session.return_value.exec.side_effect = [MagicMock(all=MagicMock(return_value=[])), MagicMock(all=MagicMock(return_value=[]))]
    response = client.post("/search/text", json={"query": ""})
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "products" in data

@patch('db.DatabaseRegistry.session')
def test_search_text_word_match(mock_session):
    class FakeProduct:
        def __init__(self, id, name, price, category_id, description=None):
            self.id = id
            self.name = name
            self.price = price
            self.category_id = category_id
            self.description = description
    mock_product = FakeProduct(1, 'Camiseta azul', 10.0, 1, 'Camiseta deportiva azul')
    mock_session.return_value.exec.side_effect = [MagicMock(all=MagicMock(return_value=[])), MagicMock(all=MagicMock(return_value=[mock_product]))]
    response = client.post("/search/text", json={"query": "azul"})
    assert response.status_code == 200
    data = response.json()
    assert any("azul" in p["name"].lower() for p in data["products"])
    assert "categories" in data

@patch('db.DatabaseRegistry.session')
def test_search_text_category_match(mock_session):
    class FakeProduct:
        def __init__(self, id, name, price, category_id, description=None):
            self.id = id
            self.name = name
            self.price = price
            self.category_id = category_id
            self.description = description
    class FakeCategory:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    mock_category = FakeCategory(1, 'camisetas')  # plural, igual que la clave del diccionario
    mock_product = FakeProduct(1, 'Camiseta blanca', 10.0, mock_category.id, 'Camiseta de algodón blanca')
    mock_session_instance = MagicMock()
    mock_session_instance.exec.side_effect = [
        MagicMock(all=MagicMock(return_value=[mock_category])),
        MagicMock(all=MagicMock(return_value=[mock_product]))
    ]
    mock_session.return_value = mock_session_instance
    response = client.post("/search/text", json={"query": "camiseta"})
    assert response.status_code == 200
    data = response.json()
    assert any("camiseta" in p["name"].lower() for p in data["products"])
    assert any(c == "camisetas" for c in data["categories"])

def test_search_text_invalid_payload():
    response = client.post("/search/text", data="notjson", headers={"Content-Type": "application/json"})
    assert response.status_code == 422

def test_search_image_invalid_file():
    response = client.post("/search/image", files={"file": ("test.txt", b"notanimage", "text/plain")})
    assert response.status_code == 400
    assert "El archivo debe ser una imagen" in response.text

def test_search_image_missing_file():
    response = client.post("/search/image", files={})
    assert response.status_code == 422

def test_search_text_db_error(monkeypatch):
    import importlib
    db_module = importlib.import_module('db')
    def broken_session():
        raise Exception("DB error simulated")
    monkeypatch.setattr(db_module.DatabaseRegistry, "session", broken_session)
    try:
        response = client.post("/search/text", json={"query": "camisetas"})
        # Si no lanza excepción, debe devolver 500 o 422
        assert response.status_code == 500 or response.status_code == 422
    except Exception as e:
        # Si lanza excepción, también es válido para cobertura de error
        assert "DB error simulated" in str(e)
