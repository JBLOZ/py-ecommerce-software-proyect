"""
Weeebhook API for receiving task completion notifications from the inference server.
This API is used to receive the results of tasks that have been processed by the inference server.
The inference server sends a POST request to this API with the task ID and the result of the task.

You can learn more about the webhook API in the following link:
https://fastapi.tiangolo.com/advanced/openapi-webhooks/
"""

from typing import List

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from services import ResultService
from db import CategoryTypes

router = APIRouter()


class Prediction(BaseModel):
    """Inference result for a single task."""

    label: int = Field(..., ge=1, le=len(CategoryTypes), example=1)
    score: float = Field(..., ge=0, le=1, example=0.97)


class TaskResult(BaseModel):
    """Task result received from the inference server."""

    task_id: str
    state: str = Field(..., example="completed")
    categories: List[Prediction]


@router.post("/webhook/task_completed", status_code=status.HTTP_202_ACCEPTED)
async def receive_task_result(payload: TaskResult):
    """Receive task completion notification from the inference server."""
    result_service = ResultService()
    result_service.store_result(payload.task_id, payload.categories)
    return {"status": "received"}
