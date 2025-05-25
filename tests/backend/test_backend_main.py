import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

class TestMainLifespan(unittest.TestCase):
    @patch('main.DatabaseRegistry')
    @patch('main.load_sample_data')
    def test_lifespan_startup_and_shutdown(self, mock_load_sample_data, mock_db_registry):
        # Mock métodos
        mock_db_registry.initialize = MagicMock()
        mock_db_registry.close = MagicMock()
        
        # Usar TestClient con contexto para disparar startup/shutdown
        with TestClient(app):
            mock_db_registry.initialize.assert_called_once()
            mock_load_sample_data.assert_called_once()
        mock_db_registry.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
