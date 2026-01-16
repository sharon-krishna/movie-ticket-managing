import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtbs.settings')

app = Celery('mtbs')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
