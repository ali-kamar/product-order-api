from rest_framework import serializers
from .models import Product, Order, OrderItem, User
from django.db import transaction
from rest_framework.exceptions import ValidationError

class ProductSerializer(serializers.ModelSerializer):
    #Meta class to define the model and fields to be serialized automatically
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock']
        read_only_fields = ['id']

    # Custom validation for the price field should start with validate_ then the field name
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value
        
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    class Meta:
        model = OrderItem
        fields = ['product_name','product_price','quantity',"item_subtotal"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])  # Hash password
        user.save()
        return user


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    
    def get_total_price(self, obj):
        order_items = obj.items.all()
        return sum(order.item_subtotal for order in order_items)
    
    class Meta:
        model = Order
        fields = ['order_id', 'user', 'created_at', 'status', 'items', 'total_price']
        read_only_fields = ['order_id', 'created_at']


class ProductInfoSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()

#here we create a serializer for creating orders, because in the OrderSerializer we have set the items field to read_only=True, which means we cannot use it to create orders directly. and if we change it we should write the serializer field which are not only the product id and this will harden the process.
class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ['product', 'quantity']

    items = OrderItemCreateSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = ['order_id','user','created_at', 'status', 'items']
        read_only_fields = ['order_id', 'created_at', 'user']

    def create(self, validated_data):
        items_data = validated_data.pop('items', None)
        if not items_data:
            raise ValidationError('Order must contain at least one item.')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for item_data in items_data:
                OrderItem.objects.create(order=order, **item_data)
        return order
    
    def update(self, instance, validated_data):
        orderitem_data = validated_data.pop('items', None)
        #this atomic block ensures that all operations within it are treated as a single transaction. If any operation fails, all changes will be rolled back, maintaining data integrity.
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if orderitem_data:
                # Clear existing items
                instance.items.all().delete()
                # Create new items
                for item in orderitem_data:
                    OrderItem.objects.create(order=instance, **item)
        return instance
