from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class Subscriber(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name=_('Email'))
    first_name = models.CharField(max_length=100, blank=True, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=100, blank=True, verbose_name=_('Last Name'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False)
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Subscribed At'))
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Confirmed At'))

    class Meta:
        verbose_name = _('Subscriber')
        verbose_name_plural = _('Subscribers')
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email

class Campaign(models.Model):
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('sending', _('Sending')),
        ('sent', _('Sent')),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=_('Campaign Name'))
    subject = models.CharField(max_length=255, verbose_name=_('Subject'))
    content = models.TextField(verbose_name=_('Content'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Email(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, related_name='emails', on_delete=models.CASCADE)
    subscriber = models.ForeignKey(Subscriber, related_name='emails', on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    opened_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Email')
        verbose_name_plural = _('Emails')
        ordering = ['-sent_at']

    def __str__(self):
        return f"Email to {self.subscriber.email} for campaign {self.campaign.name}"
