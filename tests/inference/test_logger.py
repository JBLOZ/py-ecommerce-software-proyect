import importlib
import os
import sys
import shutil

def test_logger_makedirs(tmp_path, monkeypatch):
    # Paso 1: Forzar que el directorio de logs no exista
    logs_dir = tmp_path / "logs"
    log_file = logs_dir / "inference.log"
    if logs_dir.exists():
        shutil.rmtree(logs_dir)
    monkeypatch.setattr("os.path.dirname", lambda path: str(logs_dir))
    monkeypatch.setattr("os.path.exists", lambda path: False)
    monkeypatch.setattr("os.makedirs", lambda path, exist_ok: logs_dir.mkdir(parents=True, exist_ok=True))
    # Forzar reload del módulo logger
    sys_modules_backup = sys.modules.copy()
    sys.modules.pop("inference.app.utils.logger", None)
    spec = importlib.util.spec_from_file_location("logger_tested", os.path.abspath("inference/app/utils/logger.py"))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        assert logs_dir.exists()
    finally:
        sys.modules.clear()
        sys.modules.update(sys_modules_backup)

def test_logger_add_stream_handler(monkeypatch):
    # Paso 2: Forzar que el root_logger no tenga StreamHandler
    import logging
    import importlib
    root_logger = logging.getLogger()
    # Elimina todos los StreamHandler
    root_logger.handlers = [h for h in root_logger.handlers if not isinstance(h, logging.StreamHandler)]
    monkeypatch.setattr("os.path.dirname", lambda path: "logs")
    monkeypatch.setattr("os.path.exists", lambda path: True)
    monkeypatch.setattr("os.makedirs", lambda path, exist_ok: None)
    # Forzar reload del módulo logger
    sys_modules_backup = sys.modules.copy()
    sys.modules.pop("inference.app.utils.logger", None)
    spec = importlib.util.spec_from_file_location("logger_tested", os.path.abspath("inference/app/utils/logger.py"))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        # Ahora debe haber al menos un StreamHandler
        assert any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
    finally:
        sys.modules.clear()
        sys.modules.update(sys_modules_backup)
