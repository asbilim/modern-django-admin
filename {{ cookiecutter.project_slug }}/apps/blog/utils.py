# apps/blog/utils.py
import math
from django.utils.html import strip_tags
from django.utils.text import slugify
from uuid import uuid4

def calculate_reading_time(content, wpm=200):
    """
    Calculates the estimated reading time for a given text content.
    """
    if not content:
        return 0
    
    clean_content = strip_tags(content)
    word_count = len(clean_content.split())
    
    reading_time = math.ceil(word_count / wpm)
    return reading_time

def generate_excerpt(content, length=50):
    """
    Generates a short excerpt from the content.
    """
    if not content:
        return ""
        
    clean_content = strip_tags(content)
    words = clean_content.split()
    
    if len(words) <= length:
        return " ".join(words)
        
    return " ".join(words[:length]) + "..."

def generate_unique_slug(model_instance, title, slug_field_name='slug'):
    """
    Generates a unique slug for a model instance.
    If a slug with the same title exists, it appends a unique ID.
    """
    slug = slugify(title)
    ModelClass = model_instance.__class__
    
    while ModelClass.objects.filter(**{slug_field_name: slug}).exists():
        slug = f'{slugify(title)}-{uuid4().hex[:6]}'
        
    return slug 