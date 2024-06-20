from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('analysis/', post_product),
    path('register/', register_user, name='register_user'),
    path('login/', login_user),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('history/', all_history, name='history'),
    path('product_history/', product_history, name='product_history'),
    path('graph/', graph, name='graph'),

]