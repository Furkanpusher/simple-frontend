# BURDA GERÇEKLEŞTİRİLCEK GÖREVLERİ YAPAN FONKSİYONLAR VAR 


from celery import Task
from sentence_transformers import SentenceTransformer

from celery_worker import celery_app


class PredictTask(Task):
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        if not self.model:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        return self.run(*args, **kwargs)


@celery_app.task(ignore_result=False,
                 bind=True,
                 base=PredictTask,
                 name="model")
def predict(self, sentences):
    embeddings = self.model.encode(sentences).tolist()
    res = dict(zip(sentences, embeddings))
    return res
