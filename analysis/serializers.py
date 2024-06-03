from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Product, Store


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Store
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    store = StoreSerializer()
    user = UserSerializer()

    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        store = validated_data.pop('store')
        user = validated_data.pop('user')

        vendor_code = validated_data.pop('vendor_code')
        name = validated_data.pop('name')
        price = validated_data.pop('price')
        promotion = validated_data.pop('promotion')
        date = validated_data.pop('date')

        create_product = Product.objects.create(store=store,
                                                user=user,
                                                vendor_code=vendor_code,
                                                name=name,
                                                price=price,
                                                promotion=promotion,
                                                date=date)
        create_product.save()


