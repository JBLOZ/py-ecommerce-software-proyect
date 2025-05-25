import unittest
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from PIL import Image
import io
import os

# Importamos el módulo a testear con el path correcto
from inference.app.models.squeezenet import SqueezeNet


class TestSqueezeNet(unittest.TestCase):
    
    def setUp(self):
        """Configurar test environment"""
        # Reset class variables before each test
        SqueezeNet._SqueezeNet__session = None
        SqueezeNet._SqueezeNet__input_name = None
        SqueezeNet._SqueezeNet__output_name = None
    
    def tearDown(self):
        """Limpiar después de cada test"""
        # Reset class variables after each test
        SqueezeNet._SqueezeNet__session = None
        SqueezeNet._SqueezeNet__input_name = None
        SqueezeNet._SqueezeNet__output_name = None
    
    @patch('inference.app.models.squeezenet.InferenceSession')
    def test_squeezenet_initialization(self, mock_inference_session):
        """Test de inicialización del modelo SqueezeNet"""
        # Configurar mock de session
        mock_session_instance = MagicMock()
        mock_input = MagicMock()
        mock_input.name = "input_tensor"
        mock_output = MagicMock()
        mock_output.name = "output_tensor"
        
        mock_session_instance.get_inputs.return_value = [mock_input]
        mock_session_instance.get_outputs.return_value = [mock_output]
        mock_inference_session.return_value = mock_session_instance
        
        # Crear instancia
        model_path = "/path/to/model.onnx"
        model = SqueezeNet(model_path)
        
        # Verificaciones
        mock_inference_session.assert_called_once_with(model_path)
        self.assertIsNotNone(SqueezeNet._SqueezeNet__session)
        self.assertEqual(SqueezeNet._SqueezeNet__input_name, "input_tensor")
        self.assertEqual(SqueezeNet._SqueezeNet__output_name, "output_tensor")
    
    @patch('inference.app.models.squeezenet.InferenceSession')
    def test_squeezenet_singleton_behavior(self, mock_inference_session):
        """Test de comportamiento singleton del modelo"""
        # Configurar mock
        mock_session_instance = MagicMock()
        mock_input = MagicMock()
        mock_input.name = "input_tensor"
        mock_output = MagicMock()
        mock_output.name = "output_tensor"
        
        mock_session_instance.get_inputs.return_value = [mock_input]
        mock_session_instance.get_outputs.return_value = [mock_output]
        mock_inference_session.return_value = mock_session_instance
        
        # Crear múltiples instancias
        model1 = SqueezeNet("/path/to/model.onnx")
        model2 = SqueezeNet("/path/to/model.onnx")
        
        # Verificar que la session solo se inicializa una vez
        mock_inference_session.assert_called_once()
    
    @patch('inference.app.models.squeezenet.Image')
    def test_preprocess_image(self, mock_image_class):
        """Test del preprocesamiento de imágenes"""
        # Configurar mock de PIL Image
        mock_image = MagicMock()
        mock_image_rgb = MagicMock()
        mock_image_resized = MagicMock()
        
        mock_image.convert.return_value = mock_image_rgb
        mock_image_rgb.resize.return_value = mock_image_resized
        mock_image_class.open.return_value = mock_image
        
        # Configurar array numpy mock
        test_array = np.random.rand(224, 224, 3).astype(np.float32)
        
        with patch('inference.app.models.squeezenet.np.array', return_value=test_array) as mock_np_array:
            with patch('inference.app.models.squeezenet.InferenceSession'):
                model = SqueezeNet("/path/to/model.onnx")
                
                # Test del método privado a través del método público
                image_data = b"fake image bytes"
                
                # Necesitamos mockear el método __call__ para acceder al preprocesamiento
                with patch.object(model, '_SqueezeNet__session') as mock_session:
                    mock_session.run.return_value = [np.random.rand(1, 1000, 1, 1)]
                    
                    # Llamar al método que usa preprocesamiento
                    result = model(image_data)
                    
                    # Verificaciones
                    mock_image_class.open.assert_called_once()
                    mock_image.convert.assert_called_once_with('RGB')
                    mock_image_rgb.resize.assert_called_once_with((224, 224))
    
    @patch('inference.app.models.squeezenet.InferenceSession')
    def test_model_inference_call(self, mock_inference_session):
        """Test de la inferencia del modelo"""
        # Configurar mock de session
        mock_session_instance = MagicMock()
        mock_input = MagicMock()
        mock_input.name = "input_tensor"
        mock_output = MagicMock()
        mock_output.name = "output_tensor"
        
        mock_session_instance.get_inputs.return_value = [mock_input]
        mock_session_instance.get_outputs.return_value = [mock_output]
        
        # Configurar salida del modelo (simulando 1000 clases)
        mock_output_data = np.random.rand(1, 1000, 1, 1).astype(np.float32)
        # Asegurar que las top 3 clases tengan valores altos
        mock_output_data[0, 285, 0, 0] = 0.9  # Clase más probable
        mock_output_data[0, 281, 0, 0] = 0.05  # Segunda más probable
        mock_output_data[0, 282, 0, 0] = 0.03  # Tercera más probable
        
        mock_session_instance.run.return_value = [mock_output_data]
        mock_inference_session.return_value = mock_session_instance
        
        # Crear imagen fake
        with patch('inference.app.models.squeezenet.Image') as mock_image_class:
            mock_image = MagicMock()
            mock_image_rgb = MagicMock()
            mock_image_resized = MagicMock()
            
            mock_image.convert.return_value = mock_image_rgb
            mock_image_rgb.resize.return_value = mock_image_resized
            mock_image_class.open.return_value = mock_image
            
            # Mock del array numpy
            test_array = np.random.rand(224, 224, 3).astype(np.float32)
            with patch('inference.app.models.squeezenet.np.array', return_value=test_array):
                # Crear modelo y hacer inferencia
                model = SqueezeNet("/path/to/model.onnx")
                image_data = b"fake image bytes"
                result = model(image_data)
                
                # Verificaciones
                self.assertIn("category", result)
                self.assertEqual(len(result["category"]), 3)  # Top 3 categorías
                
                # Verificar que están ordenadas por confianza descendente
                confidences = [cat["confidence"] for cat in result["category"]]
                self.assertEqual(confidences, sorted(confidences, reverse=True))
                
                # Verificar tipos de datos
                for category in result["category"]:
                    self.assertIsInstance(category["label"], int)
                    self.assertIsInstance(category["confidence"], float)
    
    @patch('inference.app.models.squeezenet.InferenceSession')
    def test_model_inference_with_zero_probabilities(self, mock_inference_session):
        """Test de inferencia con probabilidades muy bajas"""
        # Configurar mock de session
        mock_session_instance = MagicMock()
        mock_input = MagicMock()
        mock_input.name = "input_tensor"
        mock_output = MagicMock()
        mock_output.name = "output_tensor"
        
        mock_session_instance.get_inputs.return_value = [mock_input]
        mock_session_instance.get_outputs.return_value = [mock_output]
        
        # Crear salida con todas las probabilidades muy bajas
        mock_output_data = np.zeros((1, 1000, 1, 1), dtype=np.float32)
        mock_output_data[0, 0, 0, 0] = 0.001  # Muy baja pero la más alta
        mock_output_data[0, 1, 0, 0] = 0.0005
        mock_output_data[0, 2, 0, 0] = 0.0001
        
        mock_session_instance.run.return_value = [mock_output_data]
        mock_inference_session.return_value = mock_session_instance
        
        with patch('inference.app.models.squeezenet.Image') as mock_image_class:
            mock_image = MagicMock()
            mock_image_rgb = MagicMock()
            mock_image_resized = MagicMock()
            
            mock_image.convert.return_value = mock_image_rgb
            mock_image_rgb.resize.return_value = mock_image_resized
            mock_image_class.open.return_value = mock_image
            
            test_array = np.random.rand(224, 224, 3).astype(np.float32)
            with patch('inference.app.models.squeezenet.np.array', return_value=test_array):
                model = SqueezeNet("/path/to/model.onnx")
                image_data = b"fake image bytes"
                result = model(image_data)
                
                # Verificar que devuelve los top 3 a pesar de probabilidades bajas
                self.assertEqual(len(result["category"]), 3)
                self.assertGreater(result["category"][0]["confidence"], 0)


if __name__ == '__main__':
    unittest.main()
