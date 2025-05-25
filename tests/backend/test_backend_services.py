import unittest
from services import ResultService


class TestResultService(unittest.TestCase):
    def setUp(self):
        # Obtener instancia del servicio de resultados
        self.service = ResultService()
        # Limpiar todos los resultados para empezar con un estado limpio
        self.service._result_store = {}
    
    def test_singleton_pattern(self):
        """Prueba que el servicio implementa correctamente el patrón Singleton."""
        # Obtener otra instancia del servicio
        another_service = ResultService()
        
        # Verificar que ambas instancias son el mismo objeto
        self.assertIs(self.service, another_service)
    
    def test_store_and_get_result(self):
        """Prueba que se pueden almacenar y recuperar resultados correctamente."""
        # Datos de prueba
        task_id = "test_task_1"
        result = [{"label": 1, "score": 0.95}]
        
        # Almacenar resultado
        self.service.store_result(task_id, result)
        
        # Recuperar resultado
        retrieved = self.service.get_result(task_id)
        
        # Verificar que el resultado recuperado es correcto
        self.assertEqual(retrieved, result)
    
    def test_has_result(self):
        """Prueba que has_result detecta correctamente si existe un resultado."""
        # Datos de prueba
        task_id = "test_task_2"
        result = [{"label": 2, "score": 0.85}]
        
        # Verificar que inicialmente no existe el resultado
        self.assertFalse(self.service.has_result(task_id))
        
        # Almacenar resultado
        self.service.store_result(task_id, result)
        
        # Verificar que ahora sí existe el resultado
        self.assertTrue(self.service.has_result(task_id))
    
    def test_get_nonexistent_result(self):
        """Prueba que get_result devuelve None para resultados inexistentes."""
        # Verificar que se devuelve None para un task_id inexistente
        self.assertIsNone(self.service.get_result("nonexistent_task"))
    
    def test_clear_result(self):
        """Prueba que se pueden eliminar resultados individuales."""
        # Datos de prueba
        task_id = "test_task_3"
        result = [{"label": 3, "score": 0.75}]
        
        # Almacenar resultado
        self.service.store_result(task_id, result)
        
        # Verificar que existe el resultado
        self.assertTrue(self.service.has_result(task_id))
        
        # Eliminar resultado
        self.service.clear_result(task_id)
        
        # Verificar que ya no existe el resultado
        self.assertFalse(self.service.has_result(task_id))
    
    def test_clear_all(self):
        """Prueba que se pueden eliminar todos los resultados."""
        # Almacenar varios resultados
        self.service.store_result("task1", ["result1"])
        self.service.store_result("task2", ["result2"])
        self.service.store_result("task3", ["result3"])
        
        # Verificar que existen los resultados
        self.assertTrue(self.service.has_result("task1"))
        self.assertTrue(self.service.has_result("task2"))
        self.assertTrue(self.service.has_result("task3"))
        
        # Eliminar todos los resultados
        self.service.clear_all()
        
        # Verificar que ya no existen los resultados
        self.assertFalse(self.service.has_result("task1"))
        self.assertFalse(self.service.has_result("task2"))
        self.assertFalse(self.service.has_result("task3"))
    
    def test_overwrite_result(self):
        """Prueba que se pueden sobrescribir resultados existentes."""
        # Datos de prueba
        task_id = "test_task_4"
        original_result = [{"label": 1, "score": 0.70}]
        new_result = [{"label": 2, "score": 0.90}]
        
        # Almacenar resultado original
        self.service.store_result(task_id, original_result)
        
        # Verificar que se almacenó correctamente
        self.assertEqual(self.service.get_result(task_id), original_result)
        
        # Sobrescribir con nuevo resultado
        self.service.store_result(task_id, new_result)
        
        # Verificar que se actualizó correctamente
        self.assertEqual(self.service.get_result(task_id), new_result)


if __name__ == '__main__':
    unittest.main()
