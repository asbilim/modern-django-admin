from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'is_featured', 'published_at', 'view_count')
    list_filter = ('status', 'is_featured', 'created_at', 'categories')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories', 'tags')
    actions = ['approve_posts', 'archive_posts']
    
    class Meta:
        frontend_config = {
            'icon': 'file-text',
            'category': 'Blog',
            'color': '#3B82F6',
            'description': 'Manage blog posts, articles, and news.',
            'include_in_dashboard': True,
        }
        field_metadata = {
            'content': {'ui_component': 'markdown_editor'},
            'excerpt': {'ui_component': 'textarea'},
        }

    def approve_posts(self, request, queryset):
        queryset.update(status='published')
    approve_posts.short_description = "Mark selected posts as published"

    def archive_posts(self, request, queryset):
        queryset.update(status='archived')
    archive_posts.short_description = "Mark selected posts as archived"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author_name', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author_name', 'author_email')
    actions = ['approve_comments', 'reject_comments']

    class Meta:
        frontend_config = {
            'icon': 'message-square',
            'category': 'Blog',
            'color': '#6366F1',
            'description': 'Moderate comments on posts.',
            'include_in_dashboard': True,
        }

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"

    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)
    reject_comments.short_description = "Reject selected comments" 