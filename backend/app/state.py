"""
State memory for the app.
WARNING: If the app is restarted, the state will be lost.
"""

# Este módulo está en desuso. Se mantiene por compatibilidad,
# pero se recomienda usar app.services.result_service.ResultService en su lugar.
# Vea app/services/result_service.py para más detalles.

from services import ResultService


# Obtener una instancia del servicio
_result_service = ResultService()


class ResultStoreProxy:
    """Proxy para compatibilidad con código existente."""

    def __getitem__(self, key):
        return _result_service.get_result(key)

    def __setitem__(self, key, value):
        _result_service.store_result(key, value)

    def __contains__(self, key):
        return _result_service.has_result(key)

    def __delitem__(self, key):
        _result_service.clear_result(key)


# Instancia del proxy para compatibilidad
result_store = ResultStoreProxy()
