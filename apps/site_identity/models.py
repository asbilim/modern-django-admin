from django.db import models
from apps.site_config.models import SingletonModel

class SiteIdentity(SingletonModel):
    """
    A singleton model to store site-wide identity and SEO settings.
    """
    name = models.CharField(max_length=255, default='My Awesome Site', help_text="The name of the site, used in the title tag.")
    description = models.TextField(blank=True, help_text="A short description of the site for SEO purposes.")
    logo = models.ImageField(upload_to='site/', blank=True, null=True, help_text="The main logo of the site.")
    favicon = models.ImageField(upload_to='site/', blank=True, null=True, help_text="The site's favicon.")
    keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords for SEO.")

    class Meta:
        verbose_name = "Site Identity & SEO"
        verbose_name_plural = "Site Identity & SEO"

    def __str__(self):
        return "Site Identity & SEO" 