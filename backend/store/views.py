import csv
import io
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Count, Q
from django.http import FileResponse, HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from . import chatbot
from .emails import send_email_async
from .models import CartItem, Category, NewsletterSubscription, Order, OrderItem, Product, ShipmentEvent
from .serializers import CategorySerializer, ProductSerializer, RegisterSerializer, UserSerializer, CartSerializer, CartItemSerializer, OrderSerializer

class IsInventoryStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.profile.role in ("inventory_manager", "admin"))

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.annotate(product_count=Count("products")).order_by("name")
    serializer_class = CategorySerializer
    pagination_class = None

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    lookup_field = "slug"
    def get_permissions(self):
        return [permissions.AllowAny()] if self.action in ("list", "retrieve") else [IsInventoryStaff()]
    def get_queryset(self):
        qs = Product.objects.filter(active=True).select_related("category")
        q, category = self.request.query_params.get("q"), self.request.query_params.get("category")
        if q: qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q))
        if category: qs = qs.filter(category__slug=category)
        if self.request.query_params.get("featured") == "true": qs = qs.filter(featured=True)
        ordering = self.request.query_params.get("ordering", "-created_at")
        if ordering in ("price", "-price", "rating", "-rating", "name", "-created_at"): qs = qs.order_by(ordering)
        return qs

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me(request): return Response(UserSerializer(request.user).data)

@api_view(["GET", "POST", "PATCH", "DELETE"])
@permission_classes([permissions.IsAuthenticated])
def cart(request):
    current = request.user.cart
    if request.method == "GET": return Response(CartSerializer(current).data)
    product_id = request.data.get("product_id")
    if request.method == "POST":
        product = Product.objects.filter(pk=product_id, active=True).first()
        if not product: return Response({"detail": "Product not found."}, status=404)
        item, created = CartItem.objects.get_or_create(cart=current, product=product, defaults={"quantity": 0})
        item.quantity = min(product.stock, item.quantity + max(1, int(request.data.get("quantity", 1))))
        if item.quantity < 1: return Response({"detail": "Product is out of stock."}, status=400)
        item.save(); return Response(CartSerializer(current).data, status=201 if created else 200)
    item = CartItem.objects.filter(cart=current, product_id=product_id).first()
    if not item: return Response({"detail": "Cart item not found."}, status=404)
    if request.method == "DELETE": item.delete()
    else:
        qty = int(request.data.get("quantity", 1))
        if qty <= 0: item.delete()
        elif qty > item.product.stock: return Response({"detail": "Requested quantity exceeds stock."}, status=400)
        else: item.quantity = qty; item.save()
    return Response(CartSerializer(current).data)

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def checkout(request):
    data = request.data
    items_data = data.get("items", [])
    try:
        if request.user.is_authenticated and not items_data:
            items = [(x.product, x.quantity) for x in request.user.cart.items.select_related("product")]
        else:
            items = [(Product.objects.get(pk=x["product_id"], active=True), int(x["quantity"])) for x in items_data]
    except (KeyError, TypeError, ValueError, Product.DoesNotExist):
        return Response({"detail": "One or more cart items are invalid or unavailable."}, status=400)
    if not items: return Response({"detail": "Your cart is empty."}, status=400)
    required = ("customer_name", "email", "phone", "address", "city", "state", "postal_code")
    missing = [field for field in required if not data.get(field)]
    if missing: return Response({"detail": f"Missing fields: {', '.join(missing)}"}, status=400)
    with transaction.atomic():
        locked = [(Product.objects.select_for_update().get(pk=p.pk), qty) for p, qty in items]
        if any(qty < 1 or qty > product.stock for product, qty in locked): return Response({"detail": "One or more items are unavailable in the requested quantity."}, status=409)
        subtotal = sum((p.sale_price * qty for p, qty in locked), Decimal("0"))
        shipping = Decimal("0") if subtotal >= 1999 else Decimal("99")
        coins = 0
        if request.user.is_authenticated:
            requested = max(0, int(data.get("coins", 0)))
            coins = min(requested, request.user.profile.reward_coins, int((subtotal + shipping) * Decimal("0.20")))
        total = subtotal + shipping - coins
        order = Order.objects.create(user=request.user if request.user.is_authenticated else None, subtotal=subtotal, shipping=shipping, coins_redeemed=coins, total=total, payment_method=data.get("payment_method", "cod"), **{x: data[x] for x in required})
        for product, qty in locked:
            OrderItem.objects.create(order=order, product=product, product_name=product.name, sku=product.sku, price=product.sale_price, quantity=qty)
            product.stock -= qty; product.save(update_fields=["stock"])
        if request.user.is_authenticated:
            request.user.profile.reward_coins -= coins; request.user.profile.save(update_fields=["reward_coins"])
            request.user.cart.items.all().delete()
        ShipmentEvent.objects.create(order=order, status="Order placed", note="We received your order.")
    send_email_async(
        f"Order {order.number} confirmed",
        f"Thanks for ordering from ProjectNest. Your total is ₹{order.total}. Track order: {order.number}",
        [order.email],
    )
    return Response(OrderSerializer(order).data, status=201)

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def subscribe(request):
    email = str(request.data.get("email", "")).strip().lower()
    try:
        validate_email(email)
    except ValidationError:
        return Response({"detail": "Enter a valid email address."}, status=400)

    subscription, created = NewsletterSubscription.objects.get_or_create(email=email, defaults={"active": True})
    if not subscription.active:
        subscription.active = True
        subscription.save(update_fields=["active"])
        created = True
    send_email_async(
        "Welcome to ProjectNest",
        "You are subscribed to ProjectNest project drops and practical learning updates.",
        [email],
    )
    message = "Check your inbox for the ProjectNest welcome email."
    return Response({"message": message}, status=201 if created else 200)

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self): return Order.objects.filter(user=self.request.user).prefetch_related("items", "shipment_events")
    @action(detail=True, methods=["get"])
    def invoice(self, request, pk=None):
        order = self.get_object(); output = io.BytesIO(); pdf = canvas.Canvas(output, pagesize=A4)
        pdf.setTitle(f"Invoice {order.number}"); pdf.setFont("Helvetica-Bold", 20); pdf.drawString(55, 790, "ProjectNest Invoice")
        pdf.setFont("Helvetica", 10); pdf.drawString(55, 765, f"Order: {order.number}"); pdf.drawString(55, 750, f"Customer: {order.customer_name}")
        y = 710
        for item in order.items.all(): pdf.drawString(55, y, f"{item.product_name}  x{item.quantity}"); pdf.drawRightString(540, y, f"Rs. {item.total}"); y -= 22
        pdf.line(55, y, 540, y); y -= 25; pdf.drawRightString(540, y, f"Shipping: Rs. {order.shipping}"); y -= 20; pdf.setFont("Helvetica-Bold", 12); pdf.drawRightString(540, y, f"Total: Rs. {order.total}")
        pdf.showPage(); pdf.save(); output.seek(0)
        return FileResponse(output, as_attachment=True, filename=f"{order.number}.pdf")

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def chat(request):
    message = str(request.data.get("message", "")).strip()[:500]
    session_id = str(request.data.get("session_id", ""))[:80]
    if not message or not session_id: return Response({"detail": "message and session_id are required."}, status=400)
    try: return Response(chatbot.answer(message, session_id, request.user.is_authenticated))
    except Exception: return Response({"answer": "The store assistant is temporarily unavailable. Please browse the catalog or try again shortly.", "links": []}, status=503)

@api_view(["POST"])
@permission_classes([IsInventoryStaff])
def import_products(request):
    upload = request.FILES.get("file")
    if not upload: return Response({"detail": "Attach a CSV file."}, status=400)
    reader = csv.DictReader(io.StringIO(upload.read().decode("utf-8-sig")))
    count = 0
    for row in reader:
        category, _ = Category.objects.get_or_create(name=row["category"], defaults={"slug": row["category"].lower().replace(" ", "-")})
        Product.objects.update_or_create(sku=row["sku"], defaults={"category": category, "name": row["name"], "slug": row.get("slug") or row["sku"].lower(), "short_description": row.get("short_description", ""), "description": row.get("description", ""), "price": row["price"], "discount_percent": row.get("discount_percent") or 0, "stock": row.get("stock") or 0, "image_url": row.get("image_url", "")}); count += 1
    return Response({"imported": count})

@api_view(["GET"])
@permission_classes([IsInventoryStaff])
def export_products(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="projectnest-products.csv"'
    writer = csv.writer(response)
    writer.writerow(["category", "sku", "name", "slug", "short_description", "description", "price", "discount_percent", "stock", "image_url"])
    for product in Product.objects.select_related("category").order_by("category__name", "name"):
        writer.writerow([product.category.name, product.sku, product.name, product.slug, product.short_description, product.description, product.price, product.discount_percent, product.stock, product.image_url])
    return response
