from fastapi import FastAPI
from inference_controller import router as inference_router

app = FastAPI()

# Incluir el router sin prefijo para que las rutas estén en la raíz
app.include_router(inference_router)
