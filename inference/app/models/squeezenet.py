from typing import Optional
import numpy as np
from PIL import Image
from io import BytesIO
from onnxruntime import InferenceSession
import json
import urllib.request


class SqueezeNet:
    """ SqueezeNet model for image classification. """

    __session: Optional[InferenceSession] = None
    __input_name: Optional[str] = None
    __output_name: Optional[str] = None
    __imagenet_labels: Optional[list] = None

    def __init__(self, model_path: str):
        if SqueezeNet.__session is None:
            SqueezeNet.__session = InferenceSession(model_path)
            SqueezeNet.__input_name = SqueezeNet.__session.get_inputs()[0].name
            SqueezeNet.__output_name = SqueezeNet.__session.get_outputs()[0].name
            # Cargar etiquetas de ImageNet
            SqueezeNet.__imagenet_labels = self._load_imagenet_labels()

    def _load_imagenet_labels(self):
        """
        Carga las etiquetas de ImageNet desde una fuente online o local.
        """
        try:
            # Intentar cargar desde URL
            url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
            with urllib.request.urlopen(url) as response:
                labels = [line.decode('utf-8').strip() for line in response.readlines()]
            return labels
        except:
            # Fallback: usar algunas etiquetas básicas si no hay conexión
            return [
                "tench", "goldfish", "great_white_shark", "tiger_shark", "hammerhead",
                "electric_ray", "stingray", "cock", "hen", "ostrich", "brambling",
                "goldfinch", "house_finch", "junco", "indigo_bunting", "robin",
                "bulbul", "jay", "magpie", "chickadee", "water_ouzel", "kite",
                "bald_eagle", "vulture", "great_grey_owl", "European_fire_salamander",
                # ... truncado para brevedad, en caso de error usa índices
            ] + [f"class_{i}" for i in range(26, 1000)]

    def __preprocess_image(self, image_data: bytes) -> np.ndarray:
        """
        Preprocess the image data for SqueezeNet model.
        Resizes the image to 224x224, normalizes it, and converts it to a tensor.
            :param image_data: Image data in bytes.
            :return: Preprocessed image tensor.
        """
        # Open image, convert to RGB, resize and normalize
        image = Image.open(BytesIO(image_data)).convert('RGB')
        image = image.resize((224, 224))
        
        # Convert to numpy array and ensure float32 from the start
        img_array = np.array(image, dtype=np.float32)
        
        # Normalize to [0, 1] range, keeping float32
        img_array = np.divide(img_array, 255.0, dtype=np.float32)
        
        # Standard normalization for SqueezeNet (ImageNet)
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        
        # Perform normalization operations explicitly in float32
        img_array = np.subtract(img_array, mean, dtype=np.float32)
        img_array = np.divide(img_array, std, dtype=np.float32)
        
        # Transpose and add batch dimension, maintaining float32
        img_array = np.transpose(img_array, (2, 0, 1)).astype(np.float32)
        img_array = np.expand_dims(img_array, axis=0).astype(np.float32)
        
        return img_array

    def __call__(self, image_data: bytes):
        """
        Classify the image using SqueezeNet model.
            :param image_data: Image data in bytes.
            :return: Top 3 predictions with their probabilities and class names.
        """
        img_tensor = self.__preprocess_image(image_data)
        outputs = SqueezeNet.__session.run([SqueezeNet.__output_name], {SqueezeNet.__input_name: img_tensor})
        scores = outputs[0][0]
        
        # Aplicar softmax para normalizar las probabilidades
        exp_scores = np.exp(scores - np.max(scores))  # Para estabilidad numérica
        probabilities = exp_scores / np.sum(exp_scores)
        # Top 3 predictions
        top3_idx = np.argsort(probabilities)[::-1][:3]
        
        top3 = []
        for idx in top3_idx:
            idx = int(idx)  # Asegurar que sea un entero escalar
            label_name = "unknown"
            if SqueezeNet.__imagenet_labels and idx < len(SqueezeNet.__imagenet_labels):
                label_name = SqueezeNet.__imagenet_labels[idx]
            
            top3.append({
                "label": idx,
                "label_name": label_name,
                "confidence": float(probabilities[idx])
            })
        
        return top3
