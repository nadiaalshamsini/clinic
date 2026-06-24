from rest_framework import serializers
from .models import Payment, Cart, CartItem, Order, OrderItem, PaymentTransaction
from nutritionists.models import Product
from subscriptions.models import Package
from appointments.models import Appointment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'payment_id',
            'patient',
            'appointment',
            'nutritionist',
            'amount',
            'date',
            'time',
            'status',
            'type',
            'payment_method',
            'transaction_id',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['payment_id', 'created_at', 'updated_at']


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, default=None)
    package_name = serializers.CharField(source='package.name', read_only=True, default=None)
    unit_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['cart_item_id', 'product', 'product_name', 'package', 'package_name', 'appointment', 'quantity', 'unit_price']

    def get_unit_price(self, obj):
        if obj.product:
            return str(obj.product.price)
        if obj.package:
            return str(obj.package.price)
        return None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['cart_id', 'items', 'created_at']


class AddToCartSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=False, allow_null=True
    )
    package = serializers.PrimaryKeyRelatedField(
        queryset=Package.objects.all(), required=False, allow_null=True
    )
    appointment = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(), required=False, allow_null=True
    )
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        filled = sum(1 for x in [data.get('product'), data.get('package'), data.get('appointment')] if x)
        if filled > 1:
            raise serializers.ValidationError('Provide exactly one of: product, package, or appointment.')
        if filled == 0:
            raise serializers.ValidationError('Provide exactly one of: product, package, or appointment.')
        return data


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, default=None)
    package_name = serializers.CharField(source='package.name', read_only=True, default=None)
    appointment_date = serializers.DateField(source='appointment.date', read_only=True, default=None)
    appointment_time = serializers.TimeField(source='appointment.time', read_only=True, default=None)
    appointment_status = serializers.CharField(source='appointment.status', read_only=True, default=None)

    class Meta:
        model = OrderItem
        fields = [
            'order_item_id',
            'product', 'product_name',
            'package', 'package_name',
            'appointment', 'appointment_date', 'appointment_time', 'appointment_status',
            'quantity', 'price',
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'patient', 'items', 'total_price', 'status', 'created_at', 'updated_at']


class OrderListSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'patient', 'items', 'total_price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['order_id', 'patient', 'total_price', 'status', 'created_at', 'updated_at']


class PaymentTransactionSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), source='order', write_only=True
    )

    class Meta:
        model = PaymentTransaction
        fields = ['id', 'transaction_id', 'order_id', 'submitted_at']
        read_only_fields = ['id', 'submitted_at']
