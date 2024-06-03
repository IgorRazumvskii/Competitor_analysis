from django.urls import path
from .views import *

urlpatterns = [
    path('analysis/hello', hello_world),
]