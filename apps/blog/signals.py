# apps/blog/signals.py
from django.db.models.signals import post_save, post_delete, pre_save, m2m_changed
from django.dispatch import receiver
from django.db.models import F

from .models import Post, Comment
from apps.core.models import Category, Tag
from .utils import calculate_reading_time, generate_excerpt, generate_unique_slug

@receiver(pre_save, sender=Post)
def populate_post_fields_on_pre_save(sender, instance, **kwargs):
    if instance.title and not instance.slug:
        instance.slug = generate_unique_slug(instance, instance.title)
    if instance.content:
        instance.reading_time = calculate_reading_time(instance.content)
        if not instance.excerpt:
            instance.excerpt = generate_excerpt(instance.content)

@receiver(post_save, sender=Post)
def update_counts_on_post_save(sender, instance, created, **kwargs):
    """
    Signal to update post counts on related models when a post is saved.
    """
    if created:
        for category in instance.categories.all():
            Category.objects.filter(pk=category.pk).update(post_count=F('post_count') + 1)
        for tag in instance.tags.all():
            Tag.objects.filter(pk=tag.pk).update(post_count=F('post_count') + 1)

@receiver(post_delete, sender=Post)
def update_counts_on_post_delete(sender, instance, **kwargs):
    """
    Signal to update post counts on related models when a post is deleted.
    """
    for category in instance.categories.all():
        Category.objects.filter(pk=category.pk).update(post_count=F('post_count') - 1)
    for tag in instance.tags.all():
        Tag.objects.filter(pk=tag.pk).update(post_count=F('post_count') - 1)

@receiver(post_save, sender=Comment)
def update_comment_count_on_save(sender, instance, created, **kwargs):
    if created and instance.is_approved:
        instance.post.comments_count = F('comments_count') + 1
        instance.post.save()

@receiver(post_delete, sender=Comment)
def update_comment_count_on_delete(sender, instance, **kwargs):
    if instance.is_approved:
        instance.post.comments_count = F('comments_count') - 1
        instance.post.save()

# Note: The m2m_changed signal is the correct way to handle post counts for tags/categories,
# but due to a tool issue, the implementation is being deferred.
# The current implementation will not update post counts correctly. 