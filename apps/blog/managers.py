from django.db import models
from django.utils import timezone
from django.db.models import Count

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published', published_at__lte=timezone.now())

    def featured(self):
        return self.get_queryset().filter(is_featured=True)

    def recent(self, count=5):
        return self.get_queryset().order_by('-published_at')[:count]

    def popular(self, count=5):
        return self.get_queryset().order_by('-view_count', '-likes_count')[:count]

class ApprovedCommentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_approved=True)

    def for_post(self, post):
        return self.get_queryset().filter(post=post)

    def recent(self, count=5):
        return self.get_queryset().order_by('-created_at')[:count] 