# Python'da test et
from celery.result import AsyncResult
from main import celery_app

task_id = "c030c0d0-ffc7-4e02-ab9f-59931b98dce9"
result = AsyncResult(task_id, app=celery_app)

print(f"Status: {result.status}")    # PENDING/SUCCESS/FAILURE
print(f"Ready: {result.ready()}")    # True/False
print(f"Result: {result.get()}")     # Sonuç (eğer bitmiş ise)