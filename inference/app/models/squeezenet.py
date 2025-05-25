from typing import Optional
import numpy as np
from PIL import Image
from io import BytesIO
from onnxruntime import InferenceSession


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
        image = Image.open(BytesIO(image_data)).convert('RGB')
        image = image.resize((224, 224))
        
        img_array = np.array(image, dtype=np.float32) / 255.0
        
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        
        img_array = (img_array - mean) / std
        img_array = np.transpose(img_array, (2, 0, 1))
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array.astype(np.float32)

    def __call__(self, image_data: bytes):
        img_tensor = self.__preprocess_image(image_data)

        # Ejecutar modelo
        outputs = self.__session.run([self.__output_name],
                                    {self.__input_name: img_tensor})[0]

        # Aplanar salida (1,1000,1,1) → (1000,)
        probabilities = outputs.squeeze()

        # Top-3 índices ordenados por probabilidad descendente
        top3_idx = np.argsort(probabilities)[-3:][::-1]

        return {
            "category": [
                {"label": int(idx), "confidence": float(probabilities[idx])}
                for idx in top3_idx
            ]
        }

