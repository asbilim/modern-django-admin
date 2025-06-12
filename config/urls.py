from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.core import views as core_views

# Admin site customization
admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin/', include('admin_api.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Password Reset
    path('api/auth/password_reset/', core_views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('api/auth/password_reset/confirm/', core_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # 2FA
    path('api/auth/2fa/enable/', core_views.TwoFactorEnableView.as_view(), name='2fa_enable'),
    path('api/auth/2fa/verify/', core_views.TwoFactorVerifyView.as_view(), name='2fa_verify'),
    path('api/auth/2fa/disable/', core_views.TwoFactorDisableView.as_view(), name='2fa_disable'),
    # API Schema:
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 