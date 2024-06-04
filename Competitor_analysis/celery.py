# import os
# from celery import Celery
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Competitor_analysis.settings')
#
# app = Celery('Competitor_analysis')
# app.config_from_object('django.conf:settings', namespace='CELERY')
#
# app.autodiscover_tasks()


from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Устанавливаем модуль настроек Django для Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Competitor_analysis.settings')

app = Celery('Competitor_analysis')

# Используем строку, чтобы избежать сериализации объекта при работе с Windows
app.config_from_object('django.conf:settings', namespace='CELERY')

# Загружаем задачи из всех зарегистрированных приложений Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
