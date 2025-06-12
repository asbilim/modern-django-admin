from django.contrib import admin
from .models import Category, Tag

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