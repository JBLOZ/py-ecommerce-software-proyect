from typing import Optional
import numpy as np
from PIL import Image
from io import BytesIO
from onnxruntime import InferenceSession


class SqueezeNet:
    """ SqueezeNet model for image classification. """

    __session: Optional[InferenceSession] = None
    __input_name: Optional[str] = None
    __output_name: Optional[str] = None

    def __init__(self, model_path: str):
        if SqueezeNet.__session is None:
            SqueezeNet.__session = InferenceSession(model_path)
            SqueezeNet.__input_name = SqueezeNet.__session.get_inputs()[0].name
            SqueezeNet.__output_name = SqueezeNet.__session.get_outputs()[0].name

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
        img_array = np.array(image).astype(np.float32) / 255.0
        # Standard normalization for SqueezeNet (ImageNet)
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img_array = (img_array - mean) / std
        img_array = np.transpose(img_array, (2, 0, 1))  # CHW
        img_array = np.expand_dims(img_array, axis=0)  # batch size 1
        return img_array

    def __call__(self, image_data: bytes):
        """
        Classify the image using SqueezeNet model.
            :param image_data: Image data in bytes.
            :return: Top 3 predictions with their probabilities.
        """
        img_tensor = self.__preprocess_image(image_data)
        outputs = SqueezeNet.__session.run([SqueezeNet.__output_name], {SqueezeNet.__input_name: img_tensor})
        scores = outputs[0][0]
        # Top 3 predictions
        top3_idx = np.argsort(scores)[::-1][:3]
        top3 = [
            {"label": int(idx), "confidence": float(scores[idx])}
            for idx in top3_idx
        ]
        return top3
