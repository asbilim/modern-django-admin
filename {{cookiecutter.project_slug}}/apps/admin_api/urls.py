from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .generators import AdminAPIGenerator
from .utils import get_admin_site_config
from .views import DashboardStatsView

# Auto-generate viewsets for all registered admin models
admin_viewsets = AdminAPIGenerator.register_all()

# Create router and register viewsets
router = DefaultRouter()
for model_name, viewset in admin_viewsets.items():
    router.register(model_name, viewset, basename=model_name)

@api_view(['GET'])
def admin_site_config(request):
    """Return configuration for the entire admin site"""
    return Response(get_admin_site_config())

@api_view(['GET'])
def admin_user_info(request):
    """Return current user information and permissions"""
    if not request.user.is_authenticated:
        return Response({'authenticated': False})
    
    return Response({
        'authenticated': True,
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
        'groups': [group.name for group in request.user.groups.all()],
        'permissions': list(request.user.get_all_permissions())
    })

app_name = 'admin_api'

urlpatterns = [
    path('', admin_site_config, name='admin-site-config'),
    path('user/', admin_user_info, name='admin-user-info'),
    path('models/', include(router.urls)),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
] 