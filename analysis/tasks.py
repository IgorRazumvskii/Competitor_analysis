from celery import shared_task
from .parsec import Parser
import time
from .models import Product, Store
from django.contrib.auth.models import User
from .serializers import ProductSerializerCreate


# можно через таску сохранять данные в модель
@shared_task
def parsing(vendor_code=0, user_id=0):
    parser = Parser()
    x = parser.run(" ", "70085281")
    # print('\n\n\n', x, '\n\n\n')
    # s = ProductSerializerCreate(x)
    return parser.run(" ", "70085281")