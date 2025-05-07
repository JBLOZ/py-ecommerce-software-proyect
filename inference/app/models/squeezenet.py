from typing import Optional

import numpy as np
from onnxruntime import InferenceSession

class SqueezeNet:
    """ SqueezeNet model for image classification. """

    __session: Optional[InferenceSession] = None

    def __init__(self, model_path: str):
        if self.__session is None:
            self.__session = InferenceSession(model_path)

    def __preprocess_image(self, image_data: bytes) -> np.ndarray:
        """
        Preprocess the image data for SqueezeNet model.
        Resizes the image to 224x224, normalizes it, and converts it to a tensor.
            :param image_data: Image data in bytes.
            :return: Preprocessed image tensor.
        """

    def __call__(self, image_data: bytes):
        """
        Classify the image using SqueezeNet model.
            :param image_data: Image data in bytes.
            :return: Top 3 predictions with their probabilities.
        """
