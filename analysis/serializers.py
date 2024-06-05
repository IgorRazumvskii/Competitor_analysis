from .models import Product, Store

from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
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


class ProductSerializer(serializers.ModelSerializer):
    # user = UserSerializer()

    class Meta:
        model = Product
        fields = ['vendor_code']


class ProductSerializerCreate(serializers.ModelSerializer):
    # user = UserSerializer()

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


