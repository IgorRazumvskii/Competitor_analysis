from celery import shared_task
from .parsec import Parser
import time
from .models import Product, Store
from django.contrib.auth.models import User


# можно через таску сохранять данные в модель
@shared_task
def parsing(vendor_code=0, user_id=0):
    parser = Parser()
    # Product.objects.create(
    #     vendor_code=vendor_code,
    #     name=parser['name'],
    #     price=parser['price'],
    #     # ToDo update promotion
    #     promotion=1,
    #     # ToDo update store
    #     store=Store.objects.get(name=parser['store']),
    #     user=User.objects.get(user_id=user_id)
    #
    # )
    # TODO! Добавить сюда JSON
    return parser.parseValta("70085281")