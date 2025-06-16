from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import EmailSettings, FileStorageSettings

@receiver(post_save, sender=EmailSettings)
def clear_email_settings_cache(sender, instance, **kwargs):
    """
    Clear the cached email settings when they are updated.
    """
    cache.delete('emailsettings')

@receiver(post_save, sender=FileStorageSettings)
def clear_file_storage_settings_cache(sender, instance, **kwargs):
    """
    Clear the cached file storage settings when they are updated.
    """
    cache.delete('filestoragesettings') 