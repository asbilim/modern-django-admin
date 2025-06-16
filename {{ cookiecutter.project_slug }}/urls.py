from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView
from apps.core import views as core_views
from apps.core.auth_views import TwoFactorTokenObtainPairView

# Admin site customization
admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin/', include('admin_api.urls')),
    path('api/blog/', include('apps.blog.urls', namespace='blog')),
    {% if cookiecutter.use_shop_app == "yes" %}path('api/shop/', include('apps.shop.urls', namespace='shop')),{% endif %}
    path('api/token/', TwoFactorTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # User Profile Management
    path('api/auth/me/', core_views.UserProfileView.as_view(), name='user-profile'),
    path('api/auth/me/change-password/', core_views.ChangePasswordView.as_view(), name='change-password'),
    # 2FA Token Verification
    path('api/auth/token/verify/', core_views.TwoFactorTokenVerifyView.as_view(), name='token_verify_2fa'),
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