from django.contrib import admin
from .models import Category, Tag, AdminPreferences, RequestLog
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin

# Unregister the original User and Group admins
admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    class Meta:
        frontend_config = {
            'icon': 'user',
            'category': 'Access Control',
            'description': 'Manage system users.',
            'include_in_dashboard': True,
        }

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    class Meta:
        frontend_config = {
            'icon': 'users',
            'category': 'Access Control',
            'description': 'Manage user groups and permissions.',
            'include_in_dashboard': True,
        }

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'post_count')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    class Meta:
        frontend_config = {
            'icon': 'folder',
            'category': 'Blog',
            'color': '#F59E0B',
            'description': 'Organize posts into categories.',
            'include_in_dashboard': True,
        }
        field_metadata = {
            'description': {'ui_component': 'textarea'},
        }

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    class Meta:
        frontend_config = {
            'icon': 'tag',
            'category': 'Blog',
            'color': '#10B981',
            'description': 'Manage content tags.',
            'include_in_dashboard': True,
        }

@admin.register(AdminPreferences)
class AdminPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'density', 'notifications_enabled')
    list_filter = ('theme', 'density')
    search_fields = ('user__username',)

    class Meta:
        frontend_config = {
            'icon': 'settings',
            'category': 'Access Control',
            'description': 'Manage user-specific admin preferences.',
            'include_in_dashboard': True,
        }

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'method', 'path', 'status_code', 'user', 'ip_address', 'response_time_ms')
    list_filter = ('method', 'status_code', 'timestamp')
    search_fields = ('path', 'user__username', 'ip_address')
    readonly_fields = ('timestamp', 'method', 'path', 'status_code', 'user', 'ip_address', 'response_time_ms')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    class Meta:
        frontend_config = {
            'icon': 'activity',
            'category': 'Analytics',
            'description': 'View API request logs for analytics.',
            'include_in_dashboard': True,
        }