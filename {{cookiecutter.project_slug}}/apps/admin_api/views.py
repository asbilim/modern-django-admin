from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.contrib import admin

{% if cookiecutter.use_blog_app == 'yes' %}
from apps.blog.models import Post, Comment
{% endif %}
{% if cookiecutter.use_todo_app == 'yes' %}
from apps.todo.models import Task, Project
{% endif %}
from apps.core.models import Category, Tag

class DashboardStatsView(APIView):
    """
    Provides statistics for the admin dashboard.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Time range for "new" items (e.g., last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # === 1. Top Level Stats Cards ===
        new_users_count = User.objects.filter(date_joined__gte=thirty_days_ago).count()
        total_users_count = User.objects.count()
        
        stats = [
            {
                "title": "Total Users",
                "value": f"{total_users_count:,}",
                "change": f"+{new_users_count}",
                "icon": "users",
                "description": "Since last 30 days"
            },
        ]
        
        {% if cookiecutter.use_blog_app == 'yes' %}
        total_posts_count = Post.objects.count()
        stats.append({ 
            "title": "Total Posts", 
            "value": f"{total_posts_count:,}", 
            "change": f"+{Post.objects.filter(published_at__gte=thirty_days_ago).count()}",
            "icon": "file-text",
            "description": "Published in last 30 days"
        })
        {% endif %}
        
        {% if cookiecutter.use_todo_app == 'yes' %}
        pending_tasks_count = Task.objects.filter(status__in=['todo', 'in_progress']).count()
        total_tasks_count = Task.objects.count()
        total_projects_count = Project.objects.count()
        new_projects_count = Project.objects.filter(created_at__gte=thirty_days_ago).count()
        stats.extend([
            { 
                "title": "Pending Tasks", 
                "value": f"{pending_tasks_count}",
                "change": f"{total_tasks_count - pending_tasks_count} done",
                "icon": "clock",
                "description": f"Out of {total_tasks_count} total"
            },
            {
                "title": "Total Projects",
                "value": f"{total_projects_count}",
                "change": f"+{new_projects_count}",
                "icon": "briefcase",
                "description": "Since last 30 days"
            },
        ])
        {% endif %}

        # === 2. User Signups Over Time ===
        user_signups = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=365))
        user_signups = user_signups.annotate(month=TruncMonth('date_joined'))
        user_signups = user_signups.values('month')
        user_signups = user_signups.annotate(count=Count('id'))
        user_signups = user_signups.order_by('month')

        user_signups_over_time = [
            {'date': record['month'].strftime('%b'), 'count': record['count']}
            for record in user_signups
        ]

        # === 3. Dynamic Content Creation Stats (Pie Chart) ===
        content_creation_stats = []
        for model, model_admin in admin.site._registry.items():
            if hasattr(model_admin, 'Meta') and hasattr(model_admin.Meta, 'frontend_config'):
                frontend_config = model_admin.Meta.frontend_config
                if frontend_config.get('include_in_dashboard', False):
                    count = model.objects.count()
                    content_creation_stats.append({
                        "name": str(model._meta.verbose_name_plural),
                        "value": count
                    })
        
        # === 4. Recent Activity ===
        activity_feed = []
        {% if cookiecutter.use_blog_app == 'yes' %}
        recent_posts = Post.objects.order_by('-created_at')[:5]
        recent_comments = Comment.objects.order_by('-created_at')[:5]
        
        for post in recent_posts:
            activity_feed.append({
                'type': 'new_post',
                'title': f'New Post: "{post.title}"',
                'user': post.author.username if post.author else 'System',
                'timestamp': post.created_at
            })
        for comment in recent_comments:
            activity_feed.append({
                'type': 'new_comment',
                'title': f'New comment on "{comment.post.title}"',
                'user': comment.author_name,
                'timestamp': comment.created_at
            })
        {% endif %}
        
        # Sort combined feed by timestamp
        activity_feed.sort(key=lambda x: x['timestamp'], reverse=True)

        data = {
            "stats": stats,
            "user_signups_over_time": user_signups_over_time,
            "content_creation_stats": content_creation_stats,
            "activity_feed": activity_feed[:10] # Limit to 10 most recent activities
        }

        return Response(data)
