import importlib.util
import sys
import os
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../inference/app')))
import importlib
main = importlib.import_module('main')
app = main.app

# Test para cubrir los imports alternativos (ImportError) en inference_controller.py y main.py
def test_inference_controller_import_fallback(monkeypatch):
    # Elimina 'utils' y 'models' de sys.modules para forzar ImportError
    sys_modules_backup = sys.modules.copy()
    sys.modules.pop('utils', None)
    sys.modules.pop('models', None)
    sys.modules.pop('tasks', None)
    sys.modules.pop('inference_controller', None)
    sys.modules.pop('inference.app.utils', None)
    sys.modules.pop('inference.app.models', None)
    sys.modules.pop('inference.app.tasks', None)
    # Carga el módulo con el import relativo
    spec = importlib.util.spec_from_file_location("inference_controller_fallback", os.path.abspath("inference/app/inference_controller.py"))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        assert hasattr(module, 'router')
    finally:
        sys.modules.clear()
        sys.modules.update(sys_modules_backup)

def test_main_import_fallback(monkeypatch):
    sys_modules_backup = sys.modules.copy()
    sys.modules.pop('utils', None)
    sys.modules.pop('inference_controller', None)
    sys.modules.pop('inference.app.utils', None)
    sys.modules.pop('inference.app.inference_controller', None)
    spec = importlib.util.spec_from_file_location("main_fallback", os.path.abspath("inference/app/main.py"))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        assert hasattr(module, 'app')
        # Cubre los logs de arranque
        assert hasattr(module, 'logger')
    finally:
        sys.modules.clear()
        sys.modules.update(sys_modules_backup)

def test_main_logger_info(caplog):
    import importlib
    import inference.app.main as main_mod
    with caplog.at_level("INFO"):
        importlib.reload(main_mod)
    logs = caplog.text.lower()
    assert "iniciando aplicación de inferencia" in logs
    assert "router de inferencia configurado correctamente" in logs
