from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CategoryViewSet, ProductViewSet, OrderViewSet, RegisterView, me, cart, checkout, chat, subscribe, import_products, export_products

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet, basename="product")
router.register("orders", OrderViewSet, basename="order")
urlpatterns = [
    path("", include(router.urls)), path("auth/register/", RegisterView.as_view()),
    path("auth/token/", TokenObtainPairView.as_view()), path("auth/token/refresh/", TokenRefreshView.as_view()), path("auth/me/", me),
    path("cart/", cart), path("checkout/", checkout), path("chat/", chat), path("subscribe/", subscribe), path("inventory/import/", import_products), path("inventory/export/", export_products),
]
