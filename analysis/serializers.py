# from .models import Product, Store
#
# from rest_framework import serializers
# from .models import User
#
#
# class UserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#
#     class Meta:
#         model = User
#         fields = ('username',)
#
#     def create(self, validated_data):
#         print('create')
#         user = User.objects.create(
#             username=validated_data['username']
#         )
#
#         user.set_password(validated_data['password'])
#         user.save()
#         return user
#
#
# class ProductSerializer(serializers.ModelSerializer):
#     # user = UserSerializer()
#
#     class Meta:
#         model = Product
#         fields = ['vendor_code']
#
#
# class StoreSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Store
#         fields = ['name']
#
#
# class ProductSerializerCreate(serializers.ModelSerializer):
#     # user = UserSerializer()
#     # store = StoreSerializer()
#
#     class Meta:
#         model = Product
#         fields = ['vendor_code', 'name', 'price', 'text']
#
#     def create(self, validated_data):
#         store = validated_data.pop('store')
#         user = validated_data.pop('username')
#
#         vendor_code = validated_data.pop('vendor_code')
#         name = validated_data.pop('name')
#         price = validated_data.pop('price')
#         text = validated_data.pop('text')
#         date = validated_data.pop('date')
#
#         create_product = Product.objects.create(store=Store.objects.get(name=store),
#                                                 user=User.objects.get(username=user),
#                                                 vendor_code=vendor_code,
#                                                 name=name,
#                                                 price=price,
#                                                 text=text,
#                                                 date=date)
#         print(create_product)
#         create_product.save()
#         return create_product
#
#

from .models import Product, Store, User
from rest_framework import serializers
from celery import shared_task


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username',)

    def create(self, validated_data):
        print('create')
        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['vendor_code']


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['name']


class ProductSerializerCreate(serializers.ModelSerializer):
    # Используем вложенные сериализаторы для обработки создания связанных объектов
    store = StoreSerializer()
    user = UserSerializer()

    class Meta:
        model = Product
        fields = ['vendor_code', 'name', 'price', 'text', 'store', 'user']

    def create(self, validated_data):
        store_data = validated_data.pop('store')
        user_data = validated_data.pop('user')

        store, created = Store.objects.get_or_create(**store_data)
        user, created = User.objects.get_or_create(**user_data)

        product = Product.objects.create(store=store, user=user, **validated_data)
        product.save()
        return product

