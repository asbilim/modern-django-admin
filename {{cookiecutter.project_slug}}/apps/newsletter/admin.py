from django.contrib import admin
from .models import Subscriber, Campaign, Email

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'subscribed_at', 'confirmed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email', 'first_name', 'last_name')
    class Meta:
        frontend_config = {
            'icon': 'users',
            'category': 'Newsletter',
            'description': 'Manage newsletter subscribers.',
            'include_in_dashboard': True,
        }

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'status', 'sent_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'subject')
    class Meta:
        frontend_config = {
            'icon': 'send',
            'category': 'Newsletter',
            'description': 'Manage email campaigns.',
            'include_in_dashboard': True,
        }

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'campaign', 'sent_at', 'opened_at')
    list_filter = ('sent_at', 'opened_at')
    search_fields = ('subscriber__email', 'campaign__name')
    class Meta:
        frontend_config = {
            'icon': 'mail',
            'category': 'Newsletter',
            'description': 'View sent emails.',
            'include_in_dashboard': True,
        }
