from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid

from apps.core.models import Category, Tag
# from apps.core.mixins import UUIDMixin # Temporarily removed
from apps.blog.managers import PublishedManager, ApprovedCommentManager

# Create your models here.
def get_featured_image_upload_path(instance, filename):
    return f"blog/posts/{instance.slug}/featured_image/{filename}"

def get_og_image_upload_path(instance, filename):
    return f"blog/posts/{instance.slug}/og_image/{filename}"

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('scheduled', _('Scheduled')),
        ('archived', _('Archived')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name=_('Title'), null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_('Slug'), null=True, blank=True)
    content = models.TextField(verbose_name=_('Content'), null=True, blank=True)
    excerpt = models.TextField(blank=True, verbose_name=_('Excerpt'), default='')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name=_('Author'), null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='posts', blank=True, verbose_name=_('Categories'))
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True, verbose_name=_('Tags'))
    featured_image = models.ImageField(upload_to=get_featured_image_upload_path, blank=True, null=True, verbose_name=_('Featured Image'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name=_('Status'))
    
    is_featured = models.BooleanField(default=False, verbose_name=_('Is Featured'))
    is_sticky = models.BooleanField(default=False, verbose_name=_('Is Sticky'))
    allow_comments = models.BooleanField(default=True, verbose_name=_('Allow Comments'))
    
    view_count = models.PositiveIntegerField(default=0, verbose_name=_('View Count'))
    reading_time = models.PositiveIntegerField(default=0, help_text=_('Estimated reading time in minutes.'), verbose_name=_('Reading Time'))
    likes_count = models.PositiveIntegerField(default=0, verbose_name=_('Likes Count'))
    comments_count = models.PositiveIntegerField(default=0, verbose_name=_('Comments Count'))
    
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Published At'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    meta_title = models.CharField(max_length=200, blank=True, verbose_name=_('Meta Title'))
    meta_description = models.CharField(max_length=300, blank=True, verbose_name=_('Meta Description'))
    meta_keywords = models.CharField(max_length=200, blank=True, verbose_name=_('Meta Keywords'))
    og_image = models.ImageField(upload_to=get_og_image_upload_path, blank=True, null=True, verbose_name=_('OG Image'))

    objects = models.Manager()  # The default manager.
    published = PublishedManager()  # Our custom manager.

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def __str__(self):
        return self.title


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Post'))
    author_name = models.CharField(max_length=100, verbose_name=_('Author Name'))
    author_email = models.EmailField(verbose_name=_('Author Email'))
    author_website = models.URLField(blank=True, verbose_name=_('Author Website'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments', verbose_name=_('User'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name=_('Parent Comment'))
    content = models.TextField(verbose_name=_('Content'))
    is_approved = models.BooleanField(default=False, verbose_name=_('Is Approved'))
    
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('IP Address'))
    user_agent = models.TextField(blank=True, verbose_name=_('User Agent'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    objects = models.Manager()  # The default manager.
    approved = ApprovedCommentManager() # Our custom manager.

    class Meta:
        ordering = ['created_at']
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    def __str__(self):
        return f"Comment by {self.author_name} on {self.post}"

class PostLike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name=_('Post'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_likes', verbose_name=_('User'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']
        verbose_name = _('Post Like')
        verbose_name_plural = _('Post Likes')

    def __str__(self):
        return f"{self.user} likes {self.post}"

class PostView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views', verbose_name=_('Post'))
    ip_address = models.GenericIPAddressField(verbose_name=_('IP Address'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='post_views', verbose_name=_('User'))
    user_agent = models.TextField(blank=True, verbose_name=_('User Agent'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Post View')
        verbose_name_plural = _('Post Views')

    def __str__(self):
        return f"View on {self.post} at {self.created_at}" 