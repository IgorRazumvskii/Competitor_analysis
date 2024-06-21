from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Product, Store


class UserSerializerCreate(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        print('create')
        user = User.objects.create(
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['name']


class ProductSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format='%Y-%m-%d', read_only=True)
    store = StoreSerializer()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    class Meta:
        model = Product
        fields = ['vendor_code', 'name', 'price', 'text', 'store', 'user', 'date']


class ProductSerializerCreate(serializers.ModelSerializer):
    date = serializers.DateField(format='%Y-%m-%d', read_only=True)
    store = StoreSerializer()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)  # Используем PrimaryKeyRelatedField для многих объектов

    class Meta:
        model = Product
        fields = ['vendor_code', 'name', 'price', 'text', 'store', 'user', 'date']

    def create(self, validated_data):
        store_data = validated_data.pop('store')
        users = validated_data.pop('user')

        store, _ = Store.objects.get_or_create(**store_data)

        product = Product.objects.create(store=store, **validated_data)

        for user_data in users:
            user = User.objects.get(pk=user_data.pk)
            product.user.add(user)

        return product
