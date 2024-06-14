from celery import shared_task
from .parsec import Parser
import time
from .models import Product, Store
from django.contrib.auth.models import User
from .serializers import ProductSerializerCreate


# можно через таску сохранять данные в модель
# @shared_task
# def parsing(vendor_code=0, user_id=0):
#     parser = Parser()
#     x = parser.run(" ", "70085281")
#     for i in range(len(x)):
#         print(f'{i}')
#         serializer = ProductSerializerCreate(x[i])
#         print(serializer.data)
#         if serializer.is_valid():
#             serializer.save()
#         # print(s)
#
#     # s = ProductSerializerCreate(x)
#     return parser.run(" ", "70085281")

@shared_task
def parsing(vendor_code=0, user_id=0):
    parser = Parser()
    data = parser.run(" ", "70085281")
    for item in data:
        serializer = ProductSerializerCreate(data=item)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)
    return data