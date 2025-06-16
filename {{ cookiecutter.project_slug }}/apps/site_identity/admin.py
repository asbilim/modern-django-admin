from django.contrib import admin
from .models import SiteIdentity

@admin.register(SiteIdentity)
class SiteIdentityAdmin(admin.ModelAdmin):
    
    class Meta:
        frontend_config = {
            'icon': 'globe',
            'category': 'Site Settings',
            'description': 'Manage site-wide identity and SEO settings.'
        } 