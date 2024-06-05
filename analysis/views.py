from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Store
from .serializers import ProductSerializer, ProductSerializerCreate
from .tasks import parsing

from celery.result import AsyncResult

import json
from rest_framework.parsers import JSONParser
from io import BytesIO


@api_view(['GET', 'POST'])
def post_product(request):
    # hello.delay()
    if request.method == 'POST':
        print(request.data['vendor_code'])
        vendor_code = request.data['vendor_code']
        p = parsing.delay()
        print("\n\n\np.get:", p.get())
        result = AsyncResult(p.id)

        return Response({'task.id': p.id})
    return Response()


@api_view(['GET', 'POST'])
def check_task_status(request, task_id):
    result = AsyncResult(task_id)
    if result.ready():
        print(result.get())
        # print(result.id)
        print(result.result)
        print(result.status)
        print(result.name)
        print(result.kwargs)
        print(result.args)
        print(result.as_list())
    return Response({'task.id': task_id,
                     'status': result.status,
                     'result': result.result})


