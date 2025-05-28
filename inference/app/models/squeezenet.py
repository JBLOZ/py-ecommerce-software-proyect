from typing import Optional
import numpy as np
from PIL import Image
from io import BytesIO
from onnxruntime import InferenceSession

try:
    from utils import get_logger
except ImportError:
    from ..utils import get_logger

logger = get_logger("squeezenet_model")


class SqueezeNet:
    __session: Optional[InferenceSession] = None
    __input_name: Optional[str] = None
    __output_name: Optional[str] = None

    def __init__(self, model_path: str):
        if SqueezeNet.__session is None:
            SqueezeNet.__session = InferenceSession(model_path)
            SqueezeNet.__input_name = SqueezeNet.__session.get_inputs()[0].name
            SqueezeNet.__output_name = SqueezeNet.__session.get_outputs()[0].name

    def __preprocess_image(self, image_data: bytes) -> np.ndarray:
        try:
            image = Image.open(BytesIO(image_data)).convert('RGB')
            image = image.resize((224, 224))

            # Asegurar que todo se mantenga en float32
            img_array = np.array(image, dtype=np.float32) / np.float32(255.0)

            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

            # Normalización manteniendo float32 - operaciones explícitas
            img_array = img_array.astype(np.float32)
            mean = mean.astype(np.float32)
            std = std.astype(np.float32)
            img_array = ((img_array - mean) / std).astype(np.float32)

            img_array = np.transpose(img_array, (2, 0, 1)).astype(np.float32)
            img_array = np.expand_dims(img_array, axis=0).astype(np.float32)

            return img_array
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            # Return a tensor of zeros with the expected shape (1, 3, 224, 224)
            return np.zeros((1, 3, 224, 224), dtype=np.float32)

    def __call__(self, image_data: bytes):
        img_tensor = self.__preprocess_image(image_data)

        # Ejecutar modelo
        outputs = self.__session.run([self.__output_name], {self.__input_name: img_tensor})[0]
        logits = outputs.squeeze().astype(np.float32)

        # Convertir logits a probabilidades usando softmax
        # softmax(x) = exp(x) / sum(exp(x))
        max_logit = np.max(logits).astype(np.float32)
        exp_logits = np.exp((logits - max_logit).astype(np.float32))  # Estabilidad numérica
        probabilities = (exp_logits / np.sum(exp_logits)).astype(np.float32)

        # Top-3 índices ordenados por probabilidad descendente
        top3_idx = np.argsort(probabilities)[-3:][::-1]

        return {
            "category": [
                {
                    "label": int(idx) + 1,
                    "confidence": f"{probabilities[idx]:.10f}"
                }
                for idx in top3_idx
            ]
        }
