from django.contrib import admin
from .models import Category, Tag
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
            'description': 'Manage system users.'
        }

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    class Meta:
        frontend_config = {
            'icon': 'users',
            'category': 'Access Control',
            'description': 'Manage user groups and permissions.'
        }

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    
    class Meta:
        frontend_config = {
            'icon': 'folder',
            'category': 'Configuration',
            'color': '#10B981',
            'description': 'Organize content with categories',
            'tree_view': True,
            'parent_field': 'parent'
        }

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    class Meta:
        frontend_config = {
            'icon': 'tag',
            'category': 'Configuration',
            'color': '#8B5CF6',
            'description': 'Manage content tags'
        }