"""
State memory for the app.
WARNING: If the app is restarted, the state will be lost.
"""

# Este módulo está en desuso. Se mantiene por compatibilidad,
# pero se recomienda usar app.services.result_service.ResultService en su lugar.
# Vea app/services/result_service.py para más detalles.

from typing import Dict, List, Any
from app.services.result_service import ResultService

# Obtener una instancia del servicio
_result_service = ResultService()

# Clase proxy para mantener compatibilidad con código existente
class ResultStoreProxy:
    def __getitem__(self, key):
        return _result_service.get_result(key)
    
    def __setitem__(self, key, value):
        _result_service.store_result(key, value)
    
    def __contains__(self, key):
        return _result_service.has_result(key)
    
    def __delitem__(self, key):
        _result_service.clear_result(key)

# Crear una instancia del proxy para mantener la compatibilidad
result_store = ResultStoreProxy()
