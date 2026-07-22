import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=30, default="sparkles")
    color = models.CharField(max_length=20, default="#6c5ce7")
    def __str__(self): return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    sku = models.CharField(max_length=40, unique=True)
    short_description = models.CharField(max_length=240)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveSmallIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=Decimal("4.5"))
    review_count = models.PositiveIntegerField(default=0)
    image_url = models.URLField(max_length=500, blank=True)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def sale_price(self):
        return (self.price * (Decimal(100) - self.discount_percent) / Decimal(100)).quantize(Decimal("0.01"))

    @property
    def stock_label(self):
        if self.stock == 0: return "Out of stock"
        if self.stock <= self.low_stock_threshold: return "Low stock"
        return "In stock"

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self): return self.name


class Profile(models.Model):
    ROLE_CHOICES = [("customer", "Customer"), ("inventory_manager", "Inventory manager"), ("admin", "Admin")]
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    role = models.CharField(max_length=24, choices=ROLE_CHOICES, default="customer")
    reward_coins = models.PositiveIntegerField(default=0)
    phone = models.CharField(max_length=20, blank=True)
    def __str__(self): return self.user.username


class Cart(models.Model):
    user = models.OneToOneField(User, related_name="cart", on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def subtotal(self): return sum((item.total for item in self.items.select_related("product")), Decimal("0"))


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    class Meta: unique_together = ("cart", "product")
    @property
    def total(self): return self.product.sale_price * self.quantity


class Wishlist(models.Model):
    user = models.OneToOneField(User, related_name="wishlist", on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)


class Order(models.Model):
    STATUS = [(x, x.title()) for x in ("pending", "confirmed", "packed", "shipped", "delivered", "cancelled")]
    PAYMENT = [("cod", "Cash on delivery"), ("razorpay", "Razorpay")]
    number = models.CharField(max_length=24, unique=True, editable=False)
    user = models.ForeignKey(User, related_name="orders", null=True, blank=True, on_delete=models.SET_NULL)
    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    postal_code = models.CharField(max_length=12)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    payment_method = models.CharField(max_length=20, choices=PAYMENT, default="cod")
    payment_status = models.CharField(max_length=20, default="pending")
    payment_reference = models.CharField(max_length=100, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coins_redeemed = models.PositiveIntegerField(default=0)
    coins_earned = models.PositiveIntegerField(default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tracking_number = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.number: self.number = f"PN-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)
    def __str__(self): return self.number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=160)
    sku = models.CharField(max_length=40)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    @property
    def total(self): return self.price * self.quantity


class ShipmentEvent(models.Model):
    order = models.ForeignKey(Order, related_name="shipment_events", on_delete=models.CASCADE)
    status = models.CharField(max_length=80)
    location = models.CharField(max_length=120, blank=True)
    note = models.CharField(max_length=240, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-occurred_at"]
