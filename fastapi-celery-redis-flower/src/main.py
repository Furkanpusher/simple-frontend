from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from starlette.requests import Request
from celery.result import AsyncResult
from fastapi.responses import JSONResponse
from tasks import predict


app = FastAPI()


class Task(BaseModel):
    """
    Celery task representation
    """
    task_id: str
    status: str


class ContentResponse(BaseModel):
    """
    Content Response
    """
    task_id: str
    status: str
    result: dict


class ContentRequest(BaseModel):
    """
    Request body
    """
    sentences: List[str]


@app.get("/")
async def root():
    return {"message": "Hello Embeddings"}


@app.post("/predict", response_model=Task, status_code=202)
async def predict_endpoint(request: Request, content_request: ContentRequest):

    task_id = predict.delay(content_request.sentences)

    return {"task_id": str(task_id), "status": "Processing"}


@app.get("/result/{task_id}", response_model=ContentResponse, status_code=200)
async def predict_result(task_id):
    task = AsyncResult(task_id)
    if not task.ready():
        return JSONResponse(status_code=202, content={"task_id": str(task_id), "status": "Processing"})
    result = task.get()
    return {"task_id": task_id, "status": "Success", "result": result}
