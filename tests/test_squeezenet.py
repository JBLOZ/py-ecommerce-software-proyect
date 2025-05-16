import unittest
from unittest.mock import patch
from models.squeezenet import SqueezeNet

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

    def test_call_private(self):
        # Probar que el método __call__ existe
        self.assertTrue(hasattr(self.model, '__call__'))

if __name__ == '__main__':
    unittest.main()
