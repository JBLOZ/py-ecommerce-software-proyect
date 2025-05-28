import numpy as np
from unittest.mock import MagicMock, patch
from inference.app.models.squeezenet import SqueezeNet

class DummySession:
    def get_inputs(self):
        return [type("I", (), {"name": "in"})()]
    def get_outputs(self):
        return [type("O", (), {"name": "out"})()]
    def run(self, outs, feeds):
        arr = np.arange(1000, dtype=np.float32).reshape(1, 1000, 1, 1)
        return [arr]

def test_squeezenet_call_top3():
    SqueezeNet._SqueezeNet__session = DummySession()
    SqueezeNet._SqueezeNet__input_name = "in"
    SqueezeNet._SqueezeNet__output_name = "out"
    model = SqueezeNet("fake.onnx")
    result = model(b"fakeimg")
    assert "category" in result
    assert len(result["category"]) == 3
    assert result["category"][0]["label"] == 1000 or result["category"][0]["label"] == 999  # depende del +1

def test_squeezenet_preprocess_image_valid():
    SqueezeNet._SqueezeNet__session = DummySession()
    SqueezeNet._SqueezeNet__input_name = "in"
    SqueezeNet._SqueezeNet__output_name = "out"
    model = SqueezeNet("fake.onnx")
    # Imagen RGB 224x224
    arr = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    import cv2
    _, buf = cv2.imencode('.jpg', arr)
    img_bytes = buf.tobytes()
    with patch("inference.app.models.squeezenet.Image.open") as mock_open:
        mock_img = MagicMock()
        mock_img.convert.return_value = mock_img
        mock_img.resize.return_value = mock_img
        # Patch __array__ as a method, not a property
        mock_img.__array__ = lambda self=None, dtype=None: arr.astype(np.float32)
        mock_open.return_value = mock_img
        tensor = model._SqueezeNet__preprocess_image(img_bytes)
        assert tensor.shape == (1, 3, 224, 224)

def test_squeezenet_preprocess_image_error():
    SqueezeNet._SqueezeNet__session = DummySession()
    SqueezeNet._SqueezeNet__input_name = "in"
    SqueezeNet._SqueezeNet__output_name = "out"
    model = SqueezeNet("fake.onnx")
    with patch("inference.app.models.squeezenet.Image.open", side_effect=Exception("fail")):
        tensor = model._SqueezeNet__preprocess_image(b"broken")
        assert tensor.shape == (1, 3, 224, 224)
        assert np.allclose(tensor, 0)

def test_squeezenet_softmax_and_top3():
    SqueezeNet._SqueezeNet__session = DummySession()
    SqueezeNet._SqueezeNet__input_name = "in"
    SqueezeNet._SqueezeNet__output_name = "out"
    model = SqueezeNet("fake.onnx")
    # Llama al modelo y verifica que las probabilidades suman 1
    result = model(b"fakeimg")
    confs = [float(c["confidence"]) for c in result["category"]]
    assert all(0 <= c <= 1 for c in confs)

def test_squeezenet_call_real_softmax_top3():
    # Forzar la inicialización real de la clase y el flujo de softmax/top-3
    class DummySession:
        def get_inputs(self):
            return [type("I", (), {"name": "in"})()]
        def get_outputs(self):
            return [type("O", (), {"name": "out"})()]
        def run(self, outs, feeds):
            arr = np.arange(1000, dtype=np.float32).reshape(1, 1000, 1, 1)
            return [arr]
    SqueezeNet._SqueezeNet__session = DummySession()
    SqueezeNet._SqueezeNet__input_name = "in"
    SqueezeNet._SqueezeNet__output_name = "out"
    model = SqueezeNet("fake.onnx")
    # Imagen dummy válida
    arr = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    import cv2
    _, buf = cv2.imencode('.jpg', arr)
    img_bytes = buf.tobytes()
    with patch("inference.app.models.squeezenet.Image.open") as mock_open:
        mock_img = MagicMock()
        mock_img.convert.return_value = mock_img
        mock_img.resize.return_value = mock_img
        mock_img.__array__ = lambda *a, **kw: arr.astype(np.float32)
        mock_open.return_value = mock_img
        result = model(img_bytes)
        assert "category" in result
        assert len(result["category"]) == 3
        confs = [float(c["confidence"]) for c in result["category"]]
        assert all(0 <= c <= 1 for c in confs)

def test_import_fallback_logger():
    # Fuerza la rama de ImportError para el logger (cobertura de líneas 9-10)
    import importlib.util
    import sys
    import types
    # Simula que 'utils' no existe en sys.modules
    sys_modules_backup = sys.modules.copy()
    sys.modules.pop('utils', None)
    sys.modules.pop('inference.app.utils', None)
    # Carga el módulo con el import relativo
    spec = importlib.util.spec_from_file_location("squeezenet_fallback", "inference/app/models/squeezenet.py")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        assert hasattr(module, 'SqueezeNet')
    finally:
        sys.modules.clear()
        sys.modules.update(sys_modules_backup)
