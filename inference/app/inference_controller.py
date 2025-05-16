from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
import uuid


# Inyección de dependencia para la tarea de Celery
def get_process_image_task():
    from .tasks import process_image_task
    return process_image_task

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/infer/image")
def infer_image(
    file: UploadFile = File(...),
    process_image_task=Depends(get_process_image_task)
):
    image_data = file.file.read()
    task_id = str(uuid.uuid4())
    task = process_image_task.delay(image_data, task_id)
    return JSONResponse(content={"task_id": getattr(task, 'id', task_id)})
