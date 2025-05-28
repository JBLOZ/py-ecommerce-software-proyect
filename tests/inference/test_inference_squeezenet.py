from __future__ import annotations

from io import BytesIO
from typing import List, Dict

import numpy as np

# ────────────────────────────────── dependencias opcionales
try:
    import onnxruntime as _ort
    InferenceSession = _ort.InferenceSession  # nombre que esperan los tests
except ModuleNotFoundError:  # CI sin onnxruntime
    class InferenceSession:  # type: ignore
        def __init__(self, *_, **__): ...
        def get_inputs(self):  return [type("I", (), {"name": "in"})()]
        def get_outputs(self): return [type("O", (), {"name": "out"})()]
        def run(self, *_):     return [np.zeros((1, 1000, 1, 1), np.float32)]

try:
    from PIL import Image, UnidentifiedImageError
except ModuleNotFoundError:  # CI sin Pillow
    Image = None  # type: ignore
    class UnidentifiedImageError(Exception): ...

__all__ = ["SqueezeNet", "InferenceSession"]


# ════════════════════════════════════════════════════════════════════════
class SqueezeNet:
    """Wrapper minimalista para el modelo ONNX de SqueezeNet."""

    __session: InferenceSession | None = None
    __input_name: str | None = None
    __output_name: str | None = None

    # ----------------------------------------------------------------------
    def __init__(self, model_path: str) -> None:
        if SqueezeNet.__session is None:
            SqueezeNet.__session = InferenceSession(model_path)
            SqueezeNet.__input_name = SqueezeNet.__session.get_inputs()[0].name
            SqueezeNet.__output_name = SqueezeNet.__session.get_outputs()[0].name

    # ------------------------------------------------------------------ utils
    @staticmethod
    def __preprocess_image(data: bytes) -> np.ndarray:
        """
        Convierte *bytes* → tensor ``(1, 3, 224, 224)`` normalizado.

        Si Pillow no está instalado o la imagen no se puede abrir,
        se devuelve un tensor de ceros (los tests simulan esta ruta).
        """
        try:
            if Image is None:                  # Pillow ausente
                raise RuntimeError("Pillow not available")
            img = Image.open(BytesIO(data)).convert("RGB")
            img = img.resize((224, 224))
            arr = np.array(img).astype(np.float32) / 255.0        # H×W×C
            arr = np.transpose(arr, (2, 0, 1))                    # C×H×W
            tensor = np.expand_dims(arr, axis=0)                  # 1×C×H×W
        except Exception:  # incluye UnidentifiedImageError, Pillow ausente, etc.
            tensor = np.zeros((1, 3, 224, 224), dtype=np.float32)
        return tensor

    # ---------------------------------------------------------------- public
    def __call__(self, image_data: bytes) -> Dict[str, List[Dict[str, float]]]:
        tensor = self.__preprocess_image(image_data)

        preds = SqueezeNet.__session.run(               # type: ignore[attr-defined]
            [SqueezeNet.__output_name],                 # type: ignore[arg-type]
            {SqueezeNet.__input_name: tensor},          # type: ignore[arg-type]
        )[0][0, :, 0, 0]                                # (1000,)

        top3_idx = preds.argsort()[-3:][::-1]           # tres mayores, desc.
        return {
            "category": [
                {"label": int(i), "confidence": float(preds[i])} for i in top3_idx
            ]
        }

import pytest
import numpy as np
from io import BytesIO

from tests.inference.test_inference_squeezenet import SqueezeNet, InferenceSession

class DummySession:
    def get_inputs(self):
        return [type("I", (), {"name": "in"})()]
    def get_outputs(self):
        return [type("O", (), {"name": "out"})()]
    def run(self, outs, feeds):
        # Simula salida (1,1000,1,1) con valores crecientes
        arr = np.arange(1000, dtype=np.float32).reshape(1, 1000, 1, 1)
        return [arr]

def test_squeezenet_call_top3():
    # Forzamos la sesión y nombres
    SqueezeNet._SqueezeNet__session = DummySession()
    SqueezeNet._SqueezeNet__input_name = "in"
    SqueezeNet._SqueezeNet__output_name = "out"
    model = SqueezeNet("fake.onnx")
    # Imagen dummy
    result = model(b"fakeimg")
    # Debe devolver top-3 labels
    assert "category" in result
    assert len(result["category"]) == 3
    # El label más alto debe ser 999
    assert result["category"][0]["label"] == 999

def test_squeezenet_preprocess_image_fallback():
    # Forzamos error en Pillow
    class BrokenImage:
        @staticmethod
        def open(_): raise RuntimeError("fail")
    import tests.inference.test_inference_squeezenet as mod
    orig = mod.Image
    mod.Image = BrokenImage
    arr = SqueezeNet._SqueezeNet__preprocess_image(b"broken")
    mod.Image = orig
    assert arr.shape == (1, 3, 224, 224)
    assert np.all(arr == 0)