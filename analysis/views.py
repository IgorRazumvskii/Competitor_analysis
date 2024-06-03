from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Store
from .tasks import hello


@api_view(['GET', 'POST'])
def hello_world(request):
    hello.delay()
    if request.method == 'POST':
        return Response('Hello')
    return Response('hello')


