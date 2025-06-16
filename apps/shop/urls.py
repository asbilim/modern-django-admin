from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet, EmailTemplateViewSet

app_name = 'shop'

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'email-templates', EmailTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 