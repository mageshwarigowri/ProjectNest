from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Category, Product, Cart, CartItem, Order, OrderItem, ShipmentEvent

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    class Meta: model = Category; fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    sale_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    stock_label = serializers.CharField(read_only=True)
    class Meta:
        model = Product
        fields = ["id", "category", "category_name", "name", "slug", "sku", "short_description", "description", "price", "discount_percent", "sale_price", "stock_label", "rating", "review_count", "image_url", "featured"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)
    class Meta: model = User; fields = ["username", "email", "password"]
    def create(self, validated_data): return User.objects.create_user(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="profile.role", read_only=True)
    reward_coins = serializers.IntegerField(source="profile.reward_coins", read_only=True)
    class Meta: model = User; fields = ["id", "username", "email", "role", "reward_coins"]

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(source="product", queryset=Product.objects.filter(active=True), write_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta: model = CartItem; fields = ["id", "product", "product_id", "quantity", "total"]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta: model = Cart; fields = ["id", "items", "subtotal", "updated_at"]

class ShipmentEventSerializer(serializers.ModelSerializer):
    class Meta: model = ShipmentEvent; fields = ["status", "location", "note", "occurred_at"]

class OrderItemSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta: model = OrderItem; fields = ["product_name", "sku", "price", "quantity", "total"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipment_events = ShipmentEventSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ["id", "number", "customer_name", "email", "phone", "address", "city", "state", "postal_code", "status", "payment_method", "payment_status", "subtotal", "shipping", "coins_redeemed", "coins_earned", "total", "tracking_number", "created_at", "items", "shipment_events"]

