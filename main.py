from fastapi import FastAPI
from pydantic import BaseModel
from celery.result import AsyncResult
from fastapi.responses import JSONResponse
from celery import Celery
from tasks import predict  # tasks.py'dan import et

app = FastAPI(title="Log Analyzer API", version="1.0.0")

# Celery configuration
celery_app = Celery('log_analyzer',
                   broker='redis://localhost:6379/0',    # ✅ Doğru
                   backend='redis://localhost:6379/0')   # ✅ Doğru

class LogAnalysisRequest(BaseModel):
    log_text: str

@app.get("/")
async def root():
    return {
        "message": "Log Analyzer API", 
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze-log",
            "get_result": "/result/{task_id}",
            "docs": "/docs"
        }
    }

@app.post("/analyze-log")
async def analyze_log_endpoint(log_request: LogAnalysisRequest):
    """
    Analyze log entry using Gemini LLM
    """
    task = predict.delay(log_request.log_text)   # Arka planda celery taski başladı ve daha hızlı 
    return {"task_id": str(task.id), "status": "Processing"}

@app.get("/result/{task_id}")
async def get_analysis_result(task_id: str):
    """
    Get analysis result by task ID
    """
    task_result = AsyncResult(task_id, app=celery_app) # celerydeki bu fonksiyon ile o özel Id ye sahip jobun resultunu çekiyoruz
    
    if not task_result.ready():  # hala pending aşamasında
        return JSONResponse(
            status_code=202,
            content={"task_id": task_id, "status": "Processing"}
        )
    
    if task_result.failed():
        return JSONResponse(
            status_code=500,
            content={"task_id": task_id, "status": "Failed", "error": str(task_result.info)}
        )
    
    result = task_result.get()   #r esultu aldık 
    return {
        "task_id": task_id, 
        "status": "Success", 
        "result": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)