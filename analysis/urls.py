from django.urls import path
from .views import *

urlpatterns = [
    path('analysis/hello', hello_world),
    path('<str:task_id>', check_task_status, name='task_status'),
]