from celery import Task
import google.generativeai as genai
from celery_worker import celery_app



# API key'i configure et
genai.configure(api_key='AIzaSyDUW1WnVsY0adFKaSSoeQrLVT4nAU5WmE8')

log_text = 'KOD BURAYA GİRİLECEK!'

# Model oluştur
model = genai.GenerativeModel('gemini-2.0-flash-001')


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
                 base=Analyze_Log,
                 name="model")
def predict(self, log_text):  # ✅ sentences -> log_text
    response = self.model.generate_content(  # ✅ self.model kullan
        contents=[
            {
                "role": "user", 
                "parts": [
                    {
                        "text": f"""Sen bir uzman sistem yöneticisi ve log analiz uzmanısın.
                        Aşağıdaki log mesajını analiz et ve şunları sağla:
                        
                        1. Hatanın ana sebebi
                        2. Önem seviyesi (Critical/High/Medium/Low)
                        3. Etkilenen sistem bileşenleri
                        4. Önerilen çözüm adımları
                        5. Benzer hataları önleme yöntemleri
                        
                        Log: {log_text}
                        Yanıtını JSON formatında ver."""
                    }
                ]
            }
        ],
        generation_config={  # model parametreleri 
            "temperature": 0.3,  # rastgelellik 
            "top_p": 0.8,  # olasılık 
            "top_k": 40,   # top kelime seçme sayısı 
            "max_output_tokens": 600,   # 1-2 paragraflık kısa cevap
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
    
    return response.text  # ✅ return response.text


    
