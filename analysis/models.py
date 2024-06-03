from django.db import models
from django.contrib.auth.models import User


class Store(models.Model):
    name = models.CharField(max_length=20)
    url = models.URLField()


class Product(models.Model):
    vendor_code = models.CharField(max_length=20)  # артикул
    name = models.CharField(max_length=20)
    price = models.FloatField()
    promotion = models.FloatField()  # скидка
    date = models.DateTimeField(auto_now_add=True)

    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    user = models.ManyToManyField(User)

