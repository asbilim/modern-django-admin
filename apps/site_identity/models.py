from django.db import models
from apps.site_config.models import SingletonModel

class SiteIdentity(SingletonModel):
    """
    A singleton model to store site-wide identity and SEO settings.
    """
    name = models.CharField(max_length=255, default='My Awesome Site', help_text="The name of the site, used in the title tag.")
    slogan = models.CharField(max_length=255, blank=True, help_text="A catchy slogan or tagline for the site.")
    description = models.TextField(blank=True, help_text="A short description of the site for SEO purposes.")
    logo = models.ImageField(upload_to='site/', blank=True, null=True, help_text="The main logo of the site (e.g., for light backgrounds).")
    logo_dark = models.ImageField(upload_to='site/', blank=True, null=True, help_text="An alternative logo for dark backgrounds.")
    favicon = models.ImageField(upload_to='site/', blank=True, null=True, help_text="The site's favicon.")
    keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords for SEO.")
    
    # Author and Contact Information
    author = models.CharField(max_length=100, blank=True, help_text="The name of the site's author or organization.")
    contact_email = models.EmailField(blank=True, help_text="Public contact email address.")
    phone_number = models.CharField(max_length=20, blank=True, help_text="Public contact phone number.")
    
    # Social Media Links
    twitter_url = models.URLField(blank=True, help_text="URL to Twitter profile.")
    facebook_url = models.URLField(blank=True, help_text="URL to Facebook page.")
    linkedin_url = models.URLField(blank=True, help_text="URL to LinkedIn profile.")
    github_url = models.URLField(blank=True, help_text="URL to GitHub profile.")
    instagram_url = models.URLField(blank=True, help_text="URL to Instagram profile.")

    class Meta:
        verbose_name = "Site Identity & SEO"
        verbose_name_plural = "Site Identity & SEO"

    def __str__(self):
        return "Site Identity & SEO" 