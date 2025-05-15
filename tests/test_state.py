import unittest
import state
from unittest.mock import patch, MagicMock

class TestResultStoreProxy(unittest.TestCase):
    def setUp(self):
        # Limpiar el store del ResultService real
        state._result_service._result_store = {}

    def test_set_and_get_item(self):
        state.result_store['clave'] = 'valor'
        self.assertIn('clave', state.result_store)
        self.assertEqual(state.result_store['clave'], 'valor')

    def test_contains(self):
        state.result_store['x'] = 123
        self.assertTrue('x' in state.result_store)
        self.assertFalse('y' in state.result_store)

    def test_delete_item(self):
        state.result_store['a'] = 1
        del state.result_store['a']
        self.assertFalse('a' in state.result_store)

    def test_proxy_calls_service(self):
        # Verifica que el proxy llama a los métodos correctos del servicio
        with patch.object(state._result_service, 'get_result', return_value='ok') as mock_get, \
             patch.object(state._result_service, 'store_result') as mock_store, \
             patch.object(state._result_service, 'has_result', return_value=True) as mock_has, \
             patch.object(state._result_service, 'clear_result') as mock_clear:
            state.result_store['k'] = 'v'
            mock_store.assert_called_with('k', 'v')
            _ = state.result_store['k']
            mock_get.assert_called_with('k')
            _ = 'k' in state.result_store
            mock_has.assert_called_with('k')
            del state.result_store['k']
            mock_clear.assert_called_with('k')

if __name__ == '__main__':
    unittest.main()
