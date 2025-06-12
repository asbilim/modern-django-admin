from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    
    class Meta:
        frontend_config = {
            'icon': 'file-text',
            'category': 'Content',
            'color': '#3B82F6',
            'description': 'Manage blog posts'
        } 