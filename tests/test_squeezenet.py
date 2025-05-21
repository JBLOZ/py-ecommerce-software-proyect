import unittest
from unittest.mock import patch, MagicMock
from models import SqueezeNet
from PIL import Image
import numpy as np
from io import BytesIO

class TestSqueezeNet(unittest.TestCase):
    def setUp(self):
        # Usar un path ficticio, ya que no hay modelo real para cargar en test unitario
        self.model_path = 'fake_model_path.onnx'
        # Parchear InferenceSession para evitar cargar un modelo real
        patcher = patch('models.squeezenet.InferenceSession')
        self.addCleanup(patcher.stop)
        self.mock_inference_session = patcher.start()
        self.model = SqueezeNet(self.model_path)

    def test_instance(self):
        self.assertIsInstance(self.model, SqueezeNet)

    def test_preprocess_image_private(self):
        # Probar que el método privado existe
        self.assertTrue(hasattr(self.model, '_SqueezeNet__preprocess_image'))
        # Crear imagen RGB válida en memoria
        img = Image.new('RGB', (300, 300), color='red')
        buf = BytesIO()
        img.save(buf, format='PNG')
        img_bytes = buf.getvalue()
        # No se testea el resultado exacto, solo que no lanza excepción
        try:
            result = self.model._SqueezeNet__preprocess_image(img_bytes)
            self.assertIsInstance(result, np.ndarray)
        except Exception as e:
            self.fail(f'__preprocess_image lanzó una excepción: {e}')

    def test_call_private(self):
        # Probar que el método __call__ existe
        self.assertTrue(hasattr(self.model, '__call__'))
        # Mock de la sesión y salida
        with patch.object(self.model, '_SqueezeNet__preprocess_image', return_value=np.zeros((1, 3, 224, 224))):
            with patch.object(SqueezeNet._SqueezeNet__session, 'run', return_value=[[np.array([0.1, 0.5, 0.4])]]):
                result = self.model(b'fake')
                self.assertIsInstance(result, list)
                self.assertEqual(len(result), 3)
                self.assertIn('label', result[0])
                self.assertIn('confidence', result[0])

if __name__ == '__main__':
    unittest.main()
