# Backend

Este módulo representa el backend principal de la aplicación. Este modulo es responsable de gestionar las solicitudes provenientes del frontend, acceder a la base de datos y coordinar las tareas de inferencia con el servicio externo.

## Endpoints requeridos

A continuación se detallan los endpoints mínimos que deben implementarse. Todos deben estar documentados con Swagger (FastAPI lo hace automáticamente).

> [!IMPORTANT]
> En esta práctica los endpoints deben estar documentados con el estándard OpenAPI. Otro tipo de documentación de endpoints no será aceptada como válida.

---

### `GET /health`

- **Descripción:** Permite comprobar si el backend está funcionando correctamente.
- **Respuesta esperada:**
  ```json
  {"status": "ok"}
  ```

### `GET /categories`
- **Descripción:** Devuelve una lista de categorías disponibles en el sistema.
- **Respuesta esperada:**
  ```json
  {
    "categories": [
      {"id": 1, "name": "camisetas"},
      {"id": 2, "name": "pantalones"},
      {"id": 3, "name": "zapatos"},
      ...
    ]
  }
  ```

### `GET /products`
- **Descripción:** Devuelve una lista de productos disponibles en el sistema.
- **Respuesta esperada:**
  ```json
  {
    "products": [
      {"id": 1, "name": "Camiseta blanca básica", "price": 12.99},
      {"id": 2, "name": "Pantalón de mezclilla", "price": 29.99},
      {"id": 3, "name": "Zapatos deportivos", "price": 49.99},
      ...
    ]
  }
  ```

### `POST /search/text`

- **Descripción:** Recibe una descripción en texto y devuelve una lista de productos que coincidan con la consulta, según la categoría predicha.
- **Cuerpo de la petición:**
  ```json
  {
    "query": "camiseta deportiva roja"
  }
  ```
- **Respuesta esperada:**
  ```json
  {
    "categories": ["camisetas"],
    "products": [
      {"id": 1, "name": "Camiseta deportiva roja M", "price": 19.99},
      ...
    ]
  }
  ```


### `POST /search/image`

- **Descripción:** Recibe una imagen enviada por el usuario, encola una tarea de inferencia y devuelve un `task_id`.
- **Entrada:** Imagen en `multipart/form-data`.
- **Respuesta esperada:**
  ```json
  {
    "task_id": "abc123"
  }
  ```


### `GET /tasks/{task_id}/result`

- **Descripción:** Consulta si el resultado de inferencia está disponible para la tarea indicada.
- **Respuesta cuando aún no está listo:** HTTP 202
  ```json
  {
    "status": "pending"
  }
  ```
- **Respuesta cuando la tarea está completa:** HTTP 200
  ```json
  {
    "categories": ["camisetas", "pantalones"],
    "products": [
      {"id": 1, "name": "Camiseta blanca básica", "price": 12.99}
      {"id": 3, "name": "Pantalón de mezclilla", "price": 29.99}
      ...
    ]
  }
  ```


### `POST /webhook/task_completed`

- **Descripción:** Endpoint invocado por el servicio de inferencia para notificar al backend que una tarea ha finalizado.

- **Cuerpo de la petición:**
  ```json
  {
    "task_id": "abc123",
    "state": "completed",
    "category": [
        { "label": 1, "confidence": 0.95 },
        { "label": 3, "confidence": 0.85 },
        { "label": 5, "confidence": 0.75 },
    ]
  }
  ```
- **Respuesta esperada:**
  ```json
  {"status": "received"}
  ```

## Busqueda de categorías en texto

Una de las funciones del backend es la búsqueda de categorías a partir de una descripción en texto. Este servicio **NO** depende del servicio de inferencia, sino que utiliza reglas de tokenización y búsqueda de palabras clave para determinar la categoría más probable.

- **Descripción:** El backend debe implementar un algoritmo de búsqueda de categorías basado en palabras clave.

- **Implementación sugerida:** Dado que esta funcionalidad no depende del servicio de inferencia, puede implementarse mediante un conjunto de reglas simples. A continuación se presenta una estrategia recomendada:
  1. Convertir el texto a minúsculas y eliminar tildes o signos de puntuación.
  2. Tokenizar el texto por espacios para extraer las palabras.
  3. Definir un diccionario de categorías, donde cada categoría tiene asociadas varias palabras clave. Por ejemplo:

     ```python
     category_keywords = {
         "camisetas": ["camiseta", "camisa", "polo"],
         "pantalones": ["pantalon", "jean", "vaquero", "bermudas", "chinos"],
         "zapatos": ["zapato", "zapatilla", "calzado", "tenis"]
         ...
     }
     ```

  4. Contar cuántas palabras clave de cada categoría aparecen en el texto.
  5. Ordenar las categorías por número de coincidencias y devolver la que tenga más apariciones (o un conjunto con las más probables).

- **Ejemplo de entrada:**
  ```json
  {
    "query": "Busco una camiseta deportiva roja"
  }
  ```

- **Resultado esperado:** El backend debería devolver la categoría `"camisetas"` y los productos asociados a esa categoría encontrados en la base de datos.

> [!WARNING]
> Tened en cuenta que esta no es la mejor implementación posible, pero es una solución sencilla y rápida de implementar. No es necesario utilizar técnicas avanzadas de NLP o machine learning para esta tarea.

## Devolver múltiples categorías

Tanto en la búsqueda de texto como en la búsqueda de imágenes, el backend debe ser capaz de devolver múltiples categorías. Esto es especialmente importante para la búsqueda de imágenes, donde el servicio de inferencia puede devolver varias categorías con diferentes niveles de confianza.

A la hora de establecer cuáles categorías devolver, el backend debe considerar las siguientes reglas en cada uno de los tipos de búsqueda:

- **Búsqueda de texto:** Si el algoritmo de búsqueda de categorías encuentra varias coincidencias, el backend debe devolver todas las categorías encontradas. Por ejemplo, si el texto contiene palabras clave para "camisetas" y "pantalones", el backend debe devolver ambas categorías. En este caso, no es necesario aplicar un umbral basado en la cantidad de palabras clave encontradas.

- **Búsqueda de imágenes:** El backend debe devolver las categorías que el servicio de inferencia haya devuelto siempre que la confianza de la categoría predicha sea mayor a un determinado umbral. El servicio de inferencia siempre devolverá las 3 categorías más probables, pero el backend debe filtrar aquellas que no superen el umbral.

> El umbral en la práctica debe ser un parámetro configurable, por ejemplo, con una variable de entorno o una variable global.

## Notas

- El backend deberá mantener en memoria (temporalmente) los resultados de las tareas finalizadas, por ejemplo en un diccionario `result_store`, para ser consultados por `/tasks/{task_id}/result`.
- El backend deberá consultar la base de datos para obtener los productos que correspondan a una categoría predicha (ya sea por texto o imagen).
- El modelo de base de datos debe incluir una tabla de productos con sus categorías.

Para detalles sobre la arquitectura general del sistema o cómo se comunican los servicios, consulte el archivo principal `README.md` del proyecto.