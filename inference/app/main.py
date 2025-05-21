from fastapi import FastAPI
from inference_controller import router as inference_router

app = FastAPI()

app.include_router(inference_router)
