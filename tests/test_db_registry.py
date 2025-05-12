import unittest
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from unittest.mock import patch, MagicMock

from db import DatabaseRegistry


class TestDatabaseRegistry(unittest.TestCase):
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

    def tearDown(self):
        # Restaurar el método original
        if hasattr(self, 'original_get_engine'):
            DatabaseRegistry._DatabaseRegistry__get_engine = self.original_get_engine
    
    def test_session_and_engine_creation(self):
        session = DatabaseRegistry.session()
        self.assertIsNotNone(session)
        engine = session.get_bind()
        self.assertEqual(engine.url.drivername, 'sqlite')

    def test_session_singleton(self):
        first = DatabaseRegistry.session()
        second = DatabaseRegistry.session()
        self.assertIs(first, second)


if __name__ == '__main__':
    unittest.main()