import pytest
from sqlmodel import create_engine as _create_engine, SQLModel
from backend.app.db.registry import DatabaseRegistry

@pytest.fixture(autouse=True)
def setup_sqlite(monkeypatch):
    # Forzar engine SQLite en memoria para tests
    monkeypatch.setattr(
        'backend.app.db.registry.create_engine',
        lambda url, echo: _create_engine('sqlite:///:memory:', echo=echo)
    )
    # Reiniciar sesión singleton
    DatabaseRegistry._DatabaseRegistry__session = None
    yield


def test_session_and_engine_creation():
    session = DatabaseRegistry.session
    assert session is not None
    engine = session.get_bind()
    assert engine.url.drivername == 'sqlite'


def test_session_singleton():
    first = DatabaseRegistry.session
    second = DatabaseRegistry.session
    assert first is second