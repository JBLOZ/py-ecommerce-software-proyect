import unittest
from sqlmodel import create_engine as _create_engine
import backend.app.db.registry as registry_module


class TestDatabaseRegistry(unittest.TestCase):
    def setUp(self):
        # Patch create_engine para usar sqlite en memoria
        registry_module.create_engine = lambda url, echo=True: _create_engine('sqlite:///:memory:', echo=echo)
        # Reiniciar sesión singleton
        registry_module.DatabaseRegistry._DatabaseRegistry__session = None

    def test_session_and_engine_creation(self):
        session = registry_module.DatabaseRegistry.session()
        self.assertIsNotNone(session)
        engine = session.get_bind()
        self.assertEqual(engine.url.drivername, 'sqlite')

    def test_session_singleton(self):
        first = registry_module.DatabaseRegistry.session()
        second = registry_module.DatabaseRegistry.session()
        self.assertIs(first, second)


if __name__ == '__main__':
    unittest.main()