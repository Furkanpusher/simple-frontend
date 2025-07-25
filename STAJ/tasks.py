from celery import Task
import google.generativeai as genai
import os
from dotenv import load_dotenv
from celery import Celery

# YAPAY ZEKA MODELİ VE ONUN GİBİ FONKSİYONLARDA BURDA OLUŞTURULUR


load_dotenv()  # env dosyasını yükledim

celery_app = Celery('log_analyzer',
                   broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
                   backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'))

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

model = genai.GenerativeModel('gemini-2.0-flash-001')

log_text = 'KOD BURAYA GİRİLECEK!'


class Analyze_Log(Task):
    abstract = True 
    
    def __init__(self):
        super().__init__()
        self.model = None
        
    def __call__(self, *args, **kwargs):
        if not self.model:
            self.model = genai.GenerativeModel('gemini-2.0-flash-001')
        return self.run(*args, **kwargs)

@celery_app.task(ignore_result=False,
                 bind=True, 
                 base=Analyze_Log
                )
def predict(self, log_text):  
    response = self.model.generate_content(  
        contents=[
            {
                "role": "user", 
                "parts": [
                    {
                        "text": f"""As an expert system administrator and log analysis specialist, analyze the following log message. Provide the analysis in JSON format, with all fields in Turkish:

                        1.  Hatanın ana sebebi (Root Cause of the Error)
                        2.  Önem seviyesi (Severity) - Choose from: Critical, High, Medium, Low
                        3.  Etkilenen sistem bileşenleri (Affected System Components)
                        4.  Önerilen çözüm adımları (Suggested Solution Steps)
                        5.  Benzer hataları önleme yöntemleri (Methods to Prevent Similar Errors)

                        Log: {log_text}"""
                    }
                ]
            }
        ],
        generation_config={  # model parametreleri 
            "temperature": 0.3,  # rastgelellik 
            "top_p": 0.8,  # olasılık 
            "top_k": 40,   # top kelime seçme sayısı 
            "max_output_tokens": 200,   # çok çok kısa cevap istiyorum api request hakkım bitmesin diye
            "response_mime_type": "application/json"
        },
        safety_settings=[
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", 
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
    )
    
    return response.text 



# LOGLAR DA CONTAİNER ID İLE O CONTAİNERİ İÇİNDEKİ HATA MESAJLARINI BUL, BUNLARI ÇEK container logs [container id]
# bunu 5 dakikada bir tekrarla o containerı boş bırakma yani 
# bunları gemini a gönder çıktılarını al 
# veritabanına yazcaz 

# dockerı çalıştırabilcek vim linux sunucu 

# minio - loglar buraya txt olarak gitcek (docker compose a ekle)
# paramiko sunucu ssh bağla hata log al ve minio dosya yaz 

# dosyayolu | llm_result | id | 

# orm tool migration(veri tabanlarını açıklıyosun, ilişkileri açıklıcaksın, sonra bağlıyosun) postgre fastapi için / güvenlik için 

# env (database bilgileri oraya)

# 1- ORM 
# 2- MINIO 
# 3- docker ssh bağlantısı 

# ÖNCELİK: sadece kendi dockerını 5 dk ara ile incele logları al hataları ver veritabanına yaz