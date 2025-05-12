"""
Servicio para gestionar el almacenamiento de resultados de tareas.
Este servicio proporciona métodos para almacenar y recuperar resultados de tareas
procesadas por el servicio de inferencia.
"""

from typing import Dict, List, Optional, Any


class ResultService:
    """
    Servicio para gestionar los resultados de tareas de inferencia.
    Proporciona una capa de abstracción para el almacenamiento y recuperación de resultados.
    """
    
    _instance = None
    _result_store: Dict[str, Any] = {}
    
    def __new__(cls):
        """Implementa patrón Singleton para asegurar una única instancia del servicio."""
        if cls._instance is None:
            cls._instance = super(ResultService, cls).__new__(cls)
        return cls._instance
    
    def store_result(self, task_id: str, result: Any) -> None:
        """
        Almacena el resultado de una tarea.
        
        Args:
            task_id: Identificador único de la tarea.
            result: Resultado de la tarea a almacenar.
        """
        self._result_store[task_id] = result
    
    def get_result(self, task_id: str) -> Optional[Any]:
        """
        Recupera el resultado de una tarea por su ID.
        
        Args:
            task_id: Identificador único de la tarea.
            
        Returns:
            El resultado de la tarea si existe, None en caso contrario.
        """
        return self._result_store.get(task_id)
    
    def has_result(self, task_id: str) -> bool:
        """
        Verifica si existe un resultado para una tarea.
        
        Args:
            task_id: Identificador único de la tarea.
            
        Returns:
            True si existe un resultado, False en caso contrario.
        """
        return task_id in self._result_store
    
    def clear_result(self, task_id: str) -> None:
        """
        Elimina el resultado de una tarea.
        
        Args:
            task_id: Identificador único de la tarea.
        """
        if task_id in self._result_store:
            del self._result_store[task_id]
    
    def clear_all(self) -> None:
        """Elimina todos los resultados almacenados."""
        self._result_store.clear()
