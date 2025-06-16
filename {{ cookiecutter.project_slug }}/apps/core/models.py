from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

class Category(models.Model):
    """Category model for organizing content"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    post_count = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Tag(models.Model):
    """Tag model for content tagging"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code for frontend styling')
    post_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class AdminPreferences(models.Model):
    """
    Stores individual user preferences for the admin interface.
    """
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System Default'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_preferences')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='system')
    density = models.CharField(max_length=20, choices=[('compact', 'Compact'), ('comfortable', 'Comfortable')], default='comfortable')
    notifications_enabled = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Admin Preference'
        verbose_name_plural = 'Admin Preferences'

    def __str__(self):
        return f"Preferences for {self.user.username}"

class RequestLog(models.Model):
    """
    Logs incoming API requests for analytics, excluding admin panel access.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=2048)
    status_code = models.PositiveIntegerField()
    response_time_ms = models.PositiveIntegerField(help_text="Response time in milliseconds")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Request Log'
        verbose_name_plural = 'Request Logs'

    def __str__(self):
        return f"{self.method} {self.path} {self.status_code} at {self.timestamp}" 