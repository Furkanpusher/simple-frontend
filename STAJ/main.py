from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from celery.result import AsyncResult
from celery import Celery
import os 
from dotenv import load_dotenv
from datetime import datetime
from tasks import predict, celery_app  # LLM FONKSİYONU TASKS.PY DAN GELCEK

# BU SAYFA ANA SAYFA FONKSİYONLARI ÇAĞIRIR, YAPAY ZEKA MODELİ GİBİ 

load_dotenv()

app = FastAPI(title="Log Analyzer API", version="1.0.0")

# CORS middleware ekle - Frontend entegrasyonu için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme için, üretimde daha spesifik olmalı
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Celery Worker
celery_app = Celery('log_analyzer',
                   broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),    
                   backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'))  

class LogAnalysisRequest(BaseModel):
    log_text: str

class TaskIdsRequest(BaseModel):
    task_ids: list[str]

@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """
    Ana web arayüzü - index.html dosyasını serve et
    """
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <h1>❌ Hata</h1>
        <p>index.html dosyası bulunamadı!</p>
        <p>Lütfen index.html dosyasını aynı dizine yerleştirin.</p>
        """)

@app.get("/script.js")
async def get_script():
    """
    JavaScript dosyasını serve et
    """
    try:
        with open("script.js", "r", encoding="utf-8") as f:
            js_content = f.read()
        return Response(content=js_content, media_type="application/javascript")
    except FileNotFoundError:
        return Response(content="console.error('script.js not found');", media_type="application/javascript")

@app.get("/api")
async def api_info():
    """
    API endpoints bilgileri
    """
    return {
        "message": "Log Analyzer API", 
        "version": "1.0.0",
        "endpoints": {
            "web_interface": "/",
            "api_info": "/api",
            "analyze": "/analyze-log",
            "analyze_file": "/analyze-file",
            "get_result": "/result/{task_id}",
            "get_all_results": "/get-all-results",
            "file_status": "/file-status",
            "view_file": "/view-file/{filename}",
            "docs": "/docs"
        }
    }

@app.post("/analyze-log")
async def analyze_log_endpoint(log_request: LogAnalysisRequest):
    """
    Analyze log entry using Gemini LLM
    """
    task = predict.delay(log_request.log_text)
    return {"task_id": str(task.id), "status": "Processing"}

@app.post("/analyze-file")
async def analyze_hatalar_file():
    """
    hatalar.txt dosyasını analiz et - PowerShell script'inin kullandığı endpoint
    """
    try:
        # hatalar.txt'yi oku
        with open("hatalar.txt", "r", encoding="utf-8") as f:
            hatalar = f.readlines()
        
        # Her satır için task başlat
        task_ids = []
        for hata in hatalar:
            if hata.strip():  # Boş satır değilse
                task = predict.delay(hata.strip())
                task_ids.append(str(task.id))
        
        return {"message": f"{len(task_ids)} hata analiz için gönderildi", "task_ids": task_ids}
    
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"error": "hatalar.txt dosyası bulunamadı"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Dosya okuma hatası: {str(e)}"}
        )

@app.get("/result/{task_id}")
async def get_analysis_result(task_id: str):
    """
    Task ID ile analiz sonucunu getir
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
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
    
    result = task_result.get()
    return {
        "task_id": task_id, 
        "status": "Success", 
        "result": result
    }

@app.post("/get-all-results")
async def get_all_results(request: TaskIdsRequest):
    """
    Tüm task sonuçlarını al ve analiz_sonuclari.txt'ye yaz - PowerShell uyumlu
    """
    results = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ✅ Düzeltilmiş format
    
    try:
        for task_id in request.task_ids:
            task_result = AsyncResult(task_id, app=celery_app)
            
            if task_result.ready() and not task_result.failed():
                result = task_result.get()
                results.append({
                    "task_id": task_id,
                    "timestamp": timestamp,
                    "analysis": result
                })
        
        # analiz_sonuclari.txt'ye yaz - UTF8 encoding ile
        with open("analiz_sonuclari.txt", "a", encoding="utf-8") as f:
            f.write(f"\n=== {timestamp} Analiz Sonuçları ===\n")
            for result in results:
                f.write(f"Task ID: {result['task_id']}\n")
                f.write(f"Analiz: {result['analysis']}\n")
                f.write("-" * 50 + "\n")
        
        return {"message": f"{len(results)} sonuç analiz_sonuclari.txt'ye yazıldı"}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Sonuç alma hatası: {str(e)}"}
        )

@app.get("/file-status")
async def get_file_status():
    """
    Dosya boyutlarını ve durumlarını kontrol et
    """
    def get_file_size(filename):
        try:
            size = os.path.getsize(filename)
            if size < 1024:
                return f"{size} bytes"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        except FileNotFoundError:
            return "Dosya bulunamadı"
        except Exception:
            return "Hata"
    
    def get_line_count(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 0
    
    return {
        "hatalar_size": get_file_size("hatalar.txt"),
        "hatalar_lines": get_line_count("hatalar.txt"),
        "task_log_size": get_file_size("task_log.txt"),
        "task_log_lines": get_line_count("task_log.txt"),
        "analiz_size": get_file_size("analiz_sonuclari.txt"),
        "analiz_lines": get_line_count("analiz_sonuclari.txt"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/view-file/{filename}")
async def view_file(filename: str):
    """
    Dosya içeriğini görüntüle - Güvenlik için sadece belirli dosyalara izin ver
    """
    allowed_files = ["hatalar.txt", "task_log.txt", "analiz_sonuclari.txt"]
    
    if filename not in allowed_files:
        return JSONResponse(
            status_code=403,
            content={"error": f"Bu dosyaya erişim izni yok: {filename}"}
        )
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Son 100 satırı al (çok büyük dosyalar için)
        lines = content.split('\n')
        if len(lines) > 100:
            content = '\n'.join(lines[-100:]) + f"\n\n... (Toplam {len(lines)} satır, son 100 satır gösteriliyor)"
        
        return content
    
    except FileNotFoundError:
        return f"❌ {filename} dosyası bulunamadı"
    except Exception as e:
        return f"❌ Dosya okuma hatası: {str(e)}"

@app.get("/health")
async def health_check():
    """
    Sistem sağlık kontrolü
    """
    try:
        # Celery worker durumunu kontrol et
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "celery_workers": len(active_workers) if active_workers else 0,
            "api_status": "running"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)

# bu kodu çalıştırmak için terminale uvicorn main:app --reload --port 8001