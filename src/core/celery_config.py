from celery import Celery

celery = Celery(
    "tasks",
    broker="redis://localhost:6379/1",  # Tasks queue
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)
