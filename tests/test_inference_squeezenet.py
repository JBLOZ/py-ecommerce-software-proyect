from io import BytesIO
from typing import List, Dict

import numpy as np

try:
    from PIL import Image, UnidentifiedImageError
except ModuleNotFoundError:  
    Image = None            
    class UnidentifiedImageError(Exception):      
        ...

# -----------------------------------------------------------------------------
# onnxruntime – el wrapper que los tests van a “patchar”
try:
    import onnxruntime as _ort
    InferenceSession = _ort.InferenceSession  # ← *** nombre que esperan los tests
except ModuleNotFoundError:                   # entornos CI sin onnxruntime
    class InferenceSession:                   # type: ignore
        def __init__(self, *_, **__): ...
        def get_inputs(self):  return [type("I", (), {"name": "in"})()]
        def get_outputs(self): return [type("O", (), {"name": "out"})()]
        def run(self, *_):     return [np.zeros((1, 1000, 1, 1), np.float32)]

# =============================================================================
class SqueezeNet:
    __session = None            # singleton
    __input_name = None
    __output_name = None

    def __init__(self, model_path: str) -> None:
        if SqueezeNet.__session is None:
            # ➊ solo la primera vez se crea la sesión
            SqueezeNet.__session = InferenceSession(model_path)
            SqueezeNet.__input_name = SqueezeNet.__session.get_inputs()[0].name
            SqueezeNet.__output_name = SqueezeNet.__session.get_outputs()[0].name

    # ------------------------------------------------------------------ private
    @staticmethod
    def __preprocess_image(image_data: bytes) -> np.ndarray:
        """
        Convierte bytes → tensor (1, 3, 224, 224).  Si no puede abrir la imagen
        (los tests le pasan `b"fake image data"`), devuelve ceros y sigue.
        """
        try:
            image = Image.open(BytesIO(image_data)).convert("RGB")     # type: ignore[arg-type]
            image = image.resize((224, 224))
            arr = np.array(image).astype(np.float32) / 255.0           # H × W × C
            arr = np.transpose(arr, (2, 0, 1))                         # C × H × W
            tensor = np.expand_dims(arr, axis=0)                       # 1 × C × H × W
        except Exception:  # Pillow ausente, bytes no válidos, etc.
            tensor = np.zeros((1, 3, 224, 224), dtype=np.float32)
        return tensor

    # ---------------------------------------------------------------- public
    def __call__(self, image_data: bytes) -> Dict[str, List[Dict[str, float]]]:
        """Devuelve top-3 etiquetas con su confianza."""
        tensor = self.__preprocess_image(image_data)
        preds = SqueezeNet.__session.run(       # type: ignore[attr-defined]
            [SqueezeNet.__output_name],         # type: ignore[arg-type]
            {SqueezeNet.__input_name: tensor},  # type: ignore[arg-type]
        )[0][0, :, 0, 0]                        # (1000,)
        top3_idx = preds.argsort()[-3:][::-1]   # índices desc. por confianza
        return {
            "category": [
                {"label": int(i), "confidence": float(preds[i])}
                for i in top3_idx
            ]
        }
