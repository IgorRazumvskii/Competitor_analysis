from celery import shared_task
from .parsec import Parser
import time
from .models import Product, Store
from django.contrib.auth.models import User
from .serializers import ProductSerializerCreate


# @shared_task
# def parsing(vendor_code=0, user_id=0):
#     parser = Parser()
#     data = parser.run(" ", "70085281")
#     for item in data:
#         serializer = ProductSerializerCreate(data=item)
#         if serializer.is_valid():
#             serializer.save()
#         else:
#             print(serializer.errors)
#     return data

# @shared_task
# def parsing(vendor_code=0, user_id=0):
#     parser = Parser()
#     data = parser.run(" ", "70085281")
#     for item in data:
#         username = item['user']['username']
#         user = User.objects.get(username=username)
#         item['user'] = user.pk
#         print(f'!!!!!!! {type(item["user"])}')
#         serializer = ProductSerializerCreate(data=item)
#         if serializer.is_valid():
#             serializer.save()
#         else:
#             print(serializer.errors)
#     return data

# @shared_task
# def parsing(vendor_code=0, user_id=0):
#     parser = Parser()
#     data = parser.run(" ", "70085281")
#     for item in data:
#         # Получаем пользователя по имени или создаем нового, если он не существует
#         username = 'username'
#         user, created = User.objects.get_or_create(username=username)
#
#         # Убедимся, что в данных для продукта указан правильный пользователь (pk, а не объект пользователя)
#         item['user'] = user.pk  # Используем pk пользователя
#         serializer = ProductSerializerCreate(data=item)
#         if serializer.is_valid():
#             serializer.save()
#         else:
#             print(serializer.errors)
#     return data


@shared_task
def parsing(vendor_code=0, user=0):
    parser = Parser()
    data = parser.run(" ", "70085281")
    for item in data:
        usernames = ['admin']  # Пример списка имен пользователей
        users = [User.objects.get_or_create(username=username)[0] for username in usernames]

        serializer_data = {
            "vendor_code": item['vendor_code'],
            "name": item['name'],
            "price": item['price'],
            "text": item['text'],
            "store": item['store'],
            "user": [user.pk for user in users]  # Передаем список первичных ключей пользователей
        }

        serializer = ProductSerializerCreate(data=serializer_data)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)
    return data


