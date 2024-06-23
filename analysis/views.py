import datetime
from django.utils import timezone
import time
import asyncio

from celery.result import AsyncResult

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Product, Store
from .serializers import ProductSerializer, ProductSerializerCreate, UserSerializer, UserSerializerCreate
from .tasks import parsing


#  регистрация
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    print(request)
    if request.method == 'POST':
        serializer = UserSerializerCreate(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#  авторизация
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
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def post_product(request):
    if request.method == 'POST':
        #  берем артикул
        vendor_code = request.data['vendor_code']
        #  достаем пользователя
        token = Token.objects.get(key=request.data['token'])
        user = token.user

        #  поиск товаров, которые парсились сегодня
        products = Product.objects.filter(vendor_code=vendor_code, date=timezone.now())
        if products.exists():

            for p in products:
                p.user.add(user)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)

        #  запуск парсера
        p = parsing.delay(vendor_code, user.username)
        if p == 'Error':
            return Response({"Error": "Неправильно введен артикул"})

        result = AsyncResult(p.id)

        # while result.result == None:
        #     time.sleep(1)

        timeout = 300  # Максимальное время ожидания в секундах
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = AsyncResult(p.id)
            if result.ready():
                if result.state == 'SUCCESS':
                    return Response(result.result)
                else:
                    return Response({'status': result.state})

    return Response()


# вывод результата парсера
@api_view(['POST'])
def check_task_status(request, task_id):
    result = AsyncResult(task_id)
    # if result.ready():
    return Response({'task.id': task_id,
                     'status': result.status,
                     'result': result.result})


#  история парсинга пользователя
@api_view(['POST'])
def all_history(request):
    if request.method == 'POST':
        token = Token.objects.get(key=request.data['token'])
        user = token.user
        products = Product.objects.filter(user=user)

        history = []
        dates = []
        for product in products:
            d = {}
            if product.date not in dates:
                date = product.date
                dates.append(date)
                d['date'] = date
                unic_products = []
                for i in products:
                    if i.date == date and i.vendor_code not in unic_products:
                        unic_products.append(i.vendor_code)

                d['vendor_code'] = unic_products

            if len(d.keys()) != 0:
                history.append(d)

        return Response(history)


# Вывод сравнения из истории
@api_view(['POST'])
def product_history(request):
    if request.method == 'POST':
        products = Product.objects.filter(
            vendor_code=request.data['vendor_code'],
            date=request.data['date'])

        if products.exists():
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)


#  функция для построения графиков цены товара
@api_view(['POST'])
def graph(request):
    if request.method == 'POST':
        store = Store.objects.get(name=request.data['store'])
        products = Product.objects.filter(
            vendor_code=request.data['vendor_code'],
            store=store
        )
        if products.exists():
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)

