import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carbon_friendly_api.settings')

app = Celery("carbon_friendly_api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
