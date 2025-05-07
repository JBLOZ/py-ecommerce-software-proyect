# Frontend

Este módulo contiene la interfaz de usuario de la aplicación, implementada con Gradio. El objetivo es permitir que los usuarios puedan buscar productos mediante texto o imagen y visualizar los resultados de forma clara e interactiva.

## Componentes de la interfaz

- **Input de texto** (`gr.Textbox`): Permite al usuario escribir una descripción de un producto (por ejemplo, “camiseta deportiva roja”). Esta entrada se envía al backend mediante una petición HTTP para obtener predicciones de categoría y una lista de productos asociados.

- **Input de imagen** (`gr.Image`): Permite al usuario subir una imagen de un producto. Esta imagen se envía al backend, que encola una tarea de inferencia en el servicio externo. Se muestra un loader mientras la tarea se procesa y luego los resultados.

- **Botón de búsqueda** (`gr.Button`): Dispara la ejecución de la búsqueda basada en texto, imagen o ambos.

- **Resultados de predicción** (`gr.Textbox`, `gr.List`, etc.): Muestra las categorías predichas y una lista simple de productos recomendados.

- **Indicador de carga** (`gr.Markdown`, `gr.Textbox`, `gr.Progress`, etc.): Muestra un mensaje de carga mientras se espera la respuesta del backend. Esto mejora la experiencia del usuario al proporcionar retroalimentación visual durante el procesamiento.

## Interacción del usuario final

1. **Búsqueda por texto:**
   - El usuario introduce una descripción textual.
   - Al hacer clic en el botón de búsqueda, el frontend envía una petición `POST /search/text` al backend.
   - Se muestran las categorías detectadas y los productos coincidentes.

2. **Búsqueda por imagen:**
   - El usuario sube una imagen.
   - El frontend la envía al endpoint `POST /search/image`.
   - El backend responde con un `task_id`.
   - El frontend activa un loader y comienza a consultar periódicamente (polling) el endpoint `GET /tasks/{task_id}/result`.
   - Una vez disponible el resultado, se detiene el loader y se muestran los productos clasificados.

3. **Por defecto**
    - Si el usuario no proporciona texto ni imagen, se muestran todos los productos disponibles en la base de datos.
   - Esto se logra mediante una llamada al endpoint `GET /products` al cargar la página.

## Notas adicionales

- **Reintentos y polling:**
  - El frontend realiza reintentos automáticos para obtener el resultado de una inferencia por imagen.
  - El número de intentos y el intervalo de espera se puede configurar (por ejemplo, cada 2 segundos durante un máximo de 10 intentos).

- **Manejo de errores:**
  - Si la imagen no puede ser procesada o el backend devuelve un error (código HTTP 4xx/5xx), se muestra un mensaje de error al usuario.
  - Si el `task_id` no existe o ha expirado, se indica al usuario que reintente el proceso.

- **Indicador visual durante inferencia:**
    - Se muestra una caja de texto (componente `gr.Markdown`) con un mensaje como "Clasificando imagen..." mientras se espera la respuesta del backend. Una vez recibida la inferencia, esta caja se actualiza con el mensaje correspondiente o desaparece.

- **Inferencia en navegador (opcional):**
  - Si se ha habilitado onnxruntime-web, la predicción preliminar puede mostrarse antes de que el servidor responda, mejorando la percepción de velocidad.