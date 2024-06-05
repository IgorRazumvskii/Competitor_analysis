import time
import asyncio
from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import generics, status

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Product, Store
from .serializers import ProductSerializer, ProductSerializerCreate, UserSerializer
from .tasks import parsing

from celery.result import AsyncResult


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    print('!!!')
    print(request)
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_user(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


# получение запроса на парсинг
@api_view(['POST'])
def post_product(request):
    # hello.delay()
    print(request.user)
    if request.method == 'POST':
        vendor_code = request.data['vendor_code']
        p = parsing.delay()
        result = AsyncResult(p.id)

        while result.result == None:
            time.sleep(1)
            # asyncio.sleep(1)

        return Response({'task.id': p.id,
                        'result': result.result})
    return Response()


# вывод результата парсера
@api_view(['GET', 'POST'])
def check_task_status(request, task_id):
    result = AsyncResult(task_id)
    # if result.ready():
    return Response({'task.id': task_id,
                     'status': result.status,
                     'result': result.result})


