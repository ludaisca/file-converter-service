from celery import Celery
from src.config import settings

def make_celery(app_name=__name__):
    return Celery(
        app_name,
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
        include=['src.tasks']
    )

celery_app = make_celery()
celery_app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    celery_app.start()
