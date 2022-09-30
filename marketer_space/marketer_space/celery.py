import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "marketer_space.settings")
app = Celery("marketer_space")

app.conf.enable_utc = False
app.conf.update(timezone='Asia/Yerevan')

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    'campaign': {
        'task': 'campaigns.tasks.campaign_task',
        'schedule': 30.0,
    }
}

app.autodiscover_tasks()

