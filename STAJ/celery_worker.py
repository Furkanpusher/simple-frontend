import os
from celery import Celery
from dotenv import load_dotenv
# taskler burda import edilir 

load_dotenv(".env")

celery_app = Celery('log_analyzer',
                   broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),    
                   backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'))


celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
)


from tasks import predict


# bu kodu çalıştırmak için terminale bu kodu koyunuz: celery -A celery_worker.celery_app worker --loglevel=info --pool=eventlet


# Çalışma sırası: FASTAPİ(ana kod) --> Redise task gönderir --> celery burayı dinler --> sonra da predict(LLM) çalışır 

# KISACA CELERY WORKER BURDA BAŞLATILIR