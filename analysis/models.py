from django.db import models


class Product(models.Model):
    vendor_code = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    price = models.FloatField()
    promotion = models.FloatField()
    date = models.DateField()


class Store(models.Model):
    name = models.CharField(max_length=20)
    url = models.URLField()

    product = models.ForeignKey(Product, on_delete=models.PROTECT)


class ProductData(models.Model):
    price = models.FloatField()
    promotion = models.FloatField()
    date = models.DateField()

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
