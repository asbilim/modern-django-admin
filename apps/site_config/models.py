from django.db import models
from django.core.cache import cache

class SingletonModel(models.Model):
    """
    An abstract base class for singleton models.
    Ensures that only one instance of the model exists in the database.
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def set_cache(self):
        """
        Caches the model instance. The cache key is derived from the model name.
        """
        cache.set(self.__class__.__name__.lower(), self, None)


class EmailSettings(SingletonModel):
    """
    A singleton model to store email configuration.
    These settings will override environment variables if provided.
    """
    backend = models.CharField(
        max_length=255,
        default='django.core.mail.backends.console.EmailBackend',
        help_text="The email backend to use. E.g., 'django.core.mail.backends.smtp.EmailBackend'."
    )
    host = models.CharField(max_length=255, blank=True, help_text="The email server host.")
    port = models.PositiveIntegerField(default=587, help_text="The port for the email server.")
    use_tls = models.BooleanField(default=True, help_text="Whether to use a TLS secure connection.")
    host_user = models.CharField(max_length=255, blank=True, help_text="Username for the email server.")
    host_password = models.CharField(max_length=255, blank=True, help_text="Password for the email server.")
    default_from_email = models.EmailField(blank=True, help_text="Default 'from' address for emails.")

    class Meta:
        verbose_name = "Email Settings"
        verbose_name_plural = "Email Settings"

    def __str__(self):
        return "Email Settings"


class FileStorageSettings(SingletonModel):
    """
    A singleton model to store file storage configuration, e.g., for AWS S3.
    """
    default_storage_backend = models.CharField(
        max_length=255,
        blank=True,
        help_text="Default file storage backend. E.g., 'storages.backends.s3boto3.S3Boto3Storage'."
    )
    static_storage_backend = models.CharField(
        max_length=255,
        blank=True,
        help_text="Static files storage backend. E.g., 'storages.backends.s3boto3.S3Boto3Storage'."
    )
    aws_access_key_id = models.CharField(max_length=255, blank=True)
    aws_secret_access_key = models.CharField(max_length=255, blank=True)
    aws_storage_bucket_name = models.CharField(max_length=255, blank=True)
    aws_s3_region_name = models.CharField(max_length=255, blank=True, help_text="e.g. 'us-east-1'")
    aws_s3_custom_domain = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g. 'cdn.example.com'"
    )

    class Meta:
        verbose_name = "File Storage Settings"
        verbose_name_plural = "File Storage Settings"

    def __str__(self):
        return "File Storage Settings" 