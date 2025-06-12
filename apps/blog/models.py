from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from apps.core.models import Category, Tag

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
    ]