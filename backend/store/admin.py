from django.contrib import admin
from .models import Category, Product, Profile, Order, OrderItem, ShipmentEvent

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin): list_display = ("name", "slug"); prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sku", "sale_price", "stock", "stock_label", "active")
    list_filter = ("category", "active", "featured"); search_fields = ("name", "sku"); list_editable = ("stock", "active")

class OrderItemInline(admin.TabularInline): model = OrderItem; extra = 0; readonly_fields = ("product_name", "sku", "price", "quantity")
class ShipmentInline(admin.TabularInline): model = ShipmentEvent; extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "customer_name", "status", "payment_status", "total", "created_at")
    list_filter = ("status", "payment_status", "payment_method"); search_fields = ("number", "email", "tracking_number")
    inlines = (OrderItemInline, ShipmentInline)

admin.site.register(Profile)
admin.site.site_header = "ProjectNest Administration"
