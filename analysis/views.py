import datetime
from django.utils import timezone
import time
import asyncio

from celery.result import AsyncResult

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import render

import pandas as pd

from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Product, Store
from .serializers import ProductSerializer, ProductSerializerCreate, UserSerializer, UserSerializerCreate
from .tasks import parsing
from .word2vec_model import load_model


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

        model = load_model()
        similar_vendor_code = model.wv.most_similar(vendor_code, topn=3)
        similar_words_only = [word for word, score in similar_vendor_code]
        df = pd.read_csv('analysis/data.csv')
        # pd.set_option('display.max_colwidth', None)
        similar_res = []
        for similar in similar_words_only:
            name = df['name'][df['vendor_code'] == similar]
            name = name.to_string()
            name = name.split()[1:]
            name = " ".join(name)
            similar_res.append({'name': name, 'vendor_code': similar})


        #  поиск товаров, которые парсились сегодня
        products = Product.objects.filter(vendor_code=vendor_code, date=timezone.now())
        if products.exists():

            for p in products:
                p.user.add(user)
            serializer = ProductSerializer(products, many=True)
            ans = {
                'result': serializer.data,
                'similar': similar_res
            }
            return Response(ans)
            # return Response(serializer.data)

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
                    ans = {'result': result.result,
                           'similar': similar_res}
                    return Response(ans)
                    # return Response(result.result)
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


# получение запроса на парсинг
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def post_products(request):
    if request.method == 'POST':
        #  берем артикулы
        vendor_code_1 = request.data['vendor_code_1']
        vendor_code_2 = request.data['vendor_code_2']
        #  достаем пользователя
        token = Token.objects.get(key=request.data['token'])
        user = token.user

        products_1 = Product.objects.filter(vendor_code=vendor_code_1, date=timezone.now())
        products_2 = Product.objects.filter(vendor_code=vendor_code_2, date=timezone.now())
        if products_1.exists() and products_1.exists():

            for p in products_1:
                p.user.add(user)
            serializer1 = ProductSerializer(products_1, many=True)

            for p in products_2:
                p.user.add(user)
            serializer2 = ProductSerializer(products_2, many=True)
            ans = {'result_1': serializer1.data,
                   'result_2': serializer2.data}

            return Response(ans)

        #  запуск парсера
        p1 = parsing.delay(vendor_code_1, user.username)
        p2 = parsing.delay(vendor_code_1, user.username)
        if p1 == 'Error' or p2 == 'Error':
            return Response({"Error": "Неправильно введен артикул"})

        timeout = 300  # Максимальное время ожидания в секундах
        start_time = time.time()
        while time.time() - start_time < timeout:
            result_1 = AsyncResult(p1.id)
            result_2 = AsyncResult(p2.id)

            if result_1.ready() and result_2.ready():
                if result_1.state == 'SUCCESS' and result_2.state == 'SUCCESS':
                    ans = {'result_1': result_1.result,
                           'result_2': result_2.result}
                    return Response(ans)
                else:
                    return Response({'status': result_1.state})

    return Response()

