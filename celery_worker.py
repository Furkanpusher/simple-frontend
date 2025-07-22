import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv(".env")

celery_app = Celery(
    "celery_app",
     broker="redis://localhost:6379/0",    
    backend="redis://localhost:6379/0",    
    include=["tasks"]
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
)