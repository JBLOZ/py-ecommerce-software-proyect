[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/-1JTPT80)

## Descripción General

Esta guía describe cómo implementar una aplicación web inteligente para e-commerce que permite búsqueda de productos por texto o por imagen, utilizando modelos de IA pre-entrenados. La aplicación está compuesta por varios servicios (backend, servicio de inferencia, frontend) que se comunicarán entre sí. Los estudiantes deberán integrar componentes de FastAPI, Celery, Redis, MariaDB, ONNX y Gradio, siguiendo la arquitectura propuesta. Al finalizar, se podrá desplegar toda la solución con Docker Compose y verificar su correcto funcionamiento de extremo a extremo.

## Funciones clave de la aplicación

* **Búsqueda por texto:** El usuario ingresa texto (p.ej. nombre de producto o categoría) y la aplicación devuelve productos relevantes desde la base de datos.
* **Búsqueda por imagen:** El usuario suministra una imagen de un producto; un modelo de IA clasificará la imagen para determinar su categoría, y se listarán productos similares de esa categoría.
* **Modelos IA pre-entrenados:** Se usarán modelos ya entrenados (por ejemplo, MobileNet v2 para clasificación de imágenes) sin necesidad de entrenarlos desde cero.
* **Frontend interactivo:** Una interfaz web (con Gradio) permitirá a los usuarios cargar imágenes o escribir consultas de texto y visualizar los resultados.
* **Ejecución del modelo en servidor y en navegador:** El servicio de inferencia ejecuta el modelo en el backend (usando ONNX Runtime en Python), y adicionalmente se muestra cómo podría integrarse el modelo en el navegador usando onnxruntime-web para realizar inferencia directamente en el cliente (WebAssembly).
* **Despliegue en contenedores:** Todos los componentes (base de datos, backend, servicio de IA, UI) se orquestan mediante Docker Compose para facilitar la ejecución de la aplicación completa con un solo comando.

## Arquitectura

La aplicación se divide en tres servicios principales y una base de datos, comunicándose en una arquitectura de microservicios:
* **Backend Principal (FastAPI):** Proporciona una API REST para el cliente. Gestiona las consultas de texto directamente (consultando la BD) y delega las consultas por imagen al servicio de inferencia. También coordina la obtención de resultados y los envía al frontend.
    * **Base de Datos (MariaDB):** Almacena la información de productos y categorías. Se usará MariaDB (MySQL) para persistir datos de ejemplo (productos simulados).
* **Servicio de Inferencia (FastAPI + Celery):** Microservicio dedicado a tareas de IA. Expone endpoints (por ejemplo, para *health check* o procesamiento inmediato) y define tareas Celery para ejecutar la inferencia con modelos de IA de forma asíncrona. Utiliza ONNX Runtime para ejecutar un modelo de clasificación de imágenes. Estas tareas se distribuyen a través de Redis que actúa como *message broker* y almacén de resultados.
* **Frontend (Gradio):** Interfaz web que permite al usuario final interactuar con la aplicación de forma sencilla. Incluye componentes para ingresar texto o imágenes y muestra los productos recuperados. El frontend se comunica con el backend principal (vía solicitudes HTTP internas) para enviar consultas y obtener resultados. Además, puede integrar código JavaScript/TypeScript para demostrar inferencia en el navegador con onnxruntime-web.

La comunicación entre servicios sigue este flujo general:

1. Consulta de texto: El frontend envía la consulta al endpoint REST del backend. El backend busca en la base de datos los productos cuyo nombre o descripción coinciden y devuelve la lista al frontend para mostrar.
2.	Consulta de imagen: El frontend envía la imagen al backend (vía un endpoint de carga de archivos). El backend llama al servicio de inferencia para clasificar la imagen (ya sea enviando una tarea Celery o llamando a un endpoint interno). Una vez obtenida la categoría predicha, el backend consulta la base de datos por productos de esa categoría y devuelve la lista al frontend.
3.	Inferencia en navegador (opcional): Alternativamente, el frontend puede cargar el modelo ONNX en el navegador y ejecutar la clasificación localmente (WebAssembly), luego enviar solo el resultado de categoría al backend para la búsqueda en BD. Esto reduce carga en el servidor y demuestra funcionamiento sin backend 

## Estructura inicial del proyecto

```bash
📦 proyecto-ecommerce-ia
├── README.md
├── backend
│   ├── Dockerfile
│   ├── README.md
│   └── app
│       ├── __init__.py
│       ├── api
│       │   └── webhook.py
│       ├── controllers
│       ├── db
│       │   ├── entities
│       │   │   ├── __init__.py
│       │   │   ├── category.py
│       │   │   └── product.py
│       │   └── registry.py
│       ├── main.py
│       ├── services
│       └── state.py
├── data
│   └── init.sql
├── docker-compose.yaml
├── frontend
│   ├── Dockerfile
│   ├── README.md
│   ├── app.py
│   └── requirements.txt
└── inference
    ├── Dockerfile
    ├── Dockerfile.worker
    ├── README.md
    ├── app
    │   ├── __init__.py
    │   ├── assets
    │   ├── main.py
    │   ├── models
    │   │   ├── __init__.py
    │   │   └── squeezenet.py
    │   └── tasks.py
    └── requirements.txt
```

## Evaluación

Esta práctica **se puede realizar de forma individual o en grupos de dos personas**. En caso de realizarla en grupo, ambos miembros deberán participar activamente en el desarrollo de la práctica y conocer en detalle el código implementado, y su participación deberá quedar reflejada en el repositorio.

La evaluación de la práctica se realizará mediante **pruebas automáticas** y una **revisión manual** del código que valorará el diseño de las clases y métodos, la claridad y organización del código, y el uso de buenas prácticas de programación siguiendo los conceptos vistos en la asignatura.

| Concepto                                                                                          | Peso |
|---------------------------------------------------------------------------------------------------|------|
| Implementación del servicio de inferencia (FastAPI + ONNX + Celery)                               | 25%  |
| Comunicación entre backend e inferencia (tareas encoladas, seguimiento de tareas...)              | 20%  |
| Comunicación entre frontend y backend (interacción vía API, polling, estados, errores)            | 15%  |
| Implementación correcta de los endpoints del backend (FastAPI)                                    | 10%  |
| Realización de pruebas (unitarias, de integración y cobertura)                                    | 10%  |
| Estructura modular del proyecto y uso de buenas prácticas de organización de código               | 5%   |
| Documentación técnica en cada módulo                                                              | 5%   |
| Uso de Docker para el despliegue de la aplicación completa                                        | 5%   |
| Implementación de un frontend usable e interpretable                                              | 5%   |

## Recomendaciones

### Comunicación entre backend y frontend para obtener resultados de inferencia

Cuando el usuario envía una imagen o descripción a través de la interfaz, el backend encola una tarea de inferencia. Sin embargo, el resultado de esta tarea no está disponible inmediatamente, ya que el procesamiento lo realiza un `worker` de forma asíncrona. Para manejar este flujo, deberán implementar un sistema que permita al frontend saber cuándo está listo el resultado.

1.	Al crear la tarea de inferencia, el backend debe devolver un identificador único (`task_id`) al frontend.
2.	El frontend debe mostrar un estado de carga (loader o indicador visual) mientras espera la respuesta.
3.	Para consultar si la tarea ya ha sido completada, el frontend deberá hacer peticiones periódicas (polling) a endpoint del backend que verifique el estado de la tarea (usando el `task_id`).
    - `/tasks/{task_id}/result` (GET): Devuelve el resultado de la tarea si está lista, o un mensaje indicando que aún no ha finalizado.
4.	Este endpoint debe funcionar de la siguiente forma:
    - Si la tarea todavía no está lista, debe responder con un código HTTP 202 Accepted y un mensaje indicando que el resultado no está disponible.
    - Si la tarea ya ha sido completada, debe responder con el resultado (por ejemplo, la lista de predicciones) y un código HTTP 200 OK.
5.  El servidor de inferencia notificará al backend principal cuando una tarea esté completada, a través de un webhook ya implementado (`/webhook/task_completed`). Este webhook almacena el resultado en una estructura temporal del backend (`result_store`).