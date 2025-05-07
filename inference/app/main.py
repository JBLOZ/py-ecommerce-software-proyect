import uuid

from fastapi import FastAPI, UploadFile, File
from app.tasks import process_image_task

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/infer/image")
async def infer_image(file: UploadFile = File(...)):
    image_data = await file.read()
    task_id = str(uuid.uuid4())
    process_image_task.delay(image_data, task_id)
    return {"task_id": task_id}
