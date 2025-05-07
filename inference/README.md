# Servicio de Inferencia

Este módulo contiene el servicio de inferencia que se encarga de procesar imágenes mediante modelos de IA, clasificarlas en categorías y devolver los resultados al backend principal. Utiliza FastAPI para exponer endpoints y Celery para procesar las tareas de forma asíncrona. Redis se emplea como *message broker* para las colas de tareas.

## Endpoints del servicio de inferencia

### `GET /health`

- **Descripción:** Comprueba si el servicio está activo.
- **Respuesta esperada:**
  ```json
  {
    "status": "ok"
  }
  ```

### `POST /infer/image`

- **Descripción:** Endpoint opcional para pruebas, permite recibir una imagen y ejecutar inferencia sin pasar por Celery.
- **Entrada:** Imagen en `multipart/form-data`.
- **Respuesta esperada:** Resultado inmediato de clasificación.
  ```json
  {
    "category": [
      {"label": 1, "confidence": 0.95},
      {"label": 3, "confidence": 0.83},
      {"label": 5, "confidence": 0.78}
    ]
  }
  ```

> **Nota:** En producción, el flujo estándar es a través de tareas Celery, no este endpoint.

## Tareas de Celery

### `process_image_task(image_data: bytes, task_id: str)`

Esta tarea recibe una imagen codificada y un identificador de tarea. La imagen se decodifica, se preprocesa y se pasa al modelo de clasificación (ONNX). El resultado es un conjunto de categorías con puntuaciones de confianza.

Al finalizar, el resultado se envía de vuelta al backend principal mediante un webhook `POST /webhook/task_completed`.

## Gestión de la cola

En esta práctica se define una sola cola de tareas de tipo `"image"` para inferencia. Todas las tareas de clasificación se encolan allí y son procesadas en orden por los workers disponibles.

```python
celery_app = Celery('inference', broker=REDIS_URL)
celery_app.conf.task_routes = {
    'app.tasks.process_image_task': {'queue': 'image'}
}
```

La cola se conecta a través de Redis (broker), que debe estar definido en el archivo `docker-compose.yml`.

---

## Gestión de los workers

Los workers Celery se ejecutan en contenedores separados (definidos en Docker). Para permitir escalado horizontal, es posible levantar múltiples réplicas del worker apuntando a la misma cola:

```bash
docker-compose up --scale worker_inference=3
```

Todos los workers se conectan a la misma cola y distribuyen la carga. Esto permite que múltiples tareas de inferencia se procesen simultáneamente, mejorando la capacidad de respuesta del sistema ante múltiples solicitudes.

## Consideraciones de implementación

- **Persistencia del modelo:** El modelo ONNX debe cargarse al iniciar el worker (en memoria global) y reutilizarse para cada tarea. Esto mejora el rendimiento y evita re-cargas innecesarias.

- **Webhook al backend:** Al finalizar cada tarea, el servicio de inferencia realiza una solicitud HTTP `POST` al backend, incluyendo:
  - `task_id` de la tarea procesada
  - Resultado del modelo: lista de categorías con confianza

  Esto permite al backend almacenar el resultado y notificar al frontend cuando el usuario lo solicite.

- **Tolerancia a errores:** Si la inferencia falla (imagen malformada, modelo no disponible, etc.), se recomienda capturar excepciones y registrar el error para diagnóstico. Se debe responder al webhook con un estado `failed` para manejar los errores a nivel backend.

- **Consumo de recursos:** Ejecutar tareas pesadas de inferencia puede consumir CPU y memoria. Debes asegurarte de que los workers estén aislados y limitar su uso de recursos en `docker-compose.yml` si se requiere.