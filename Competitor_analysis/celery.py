# import os
# from celery import Celery
# from django.conf import settings
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Competitor_analysis.settings')
#
# app = Celery('Competitor_analysis')
# app.config_from_object('django.conf:settings', namespace='CELERY')
#
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Competitor_analysis.settings')

app = Celery('Competitor_analysis')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
