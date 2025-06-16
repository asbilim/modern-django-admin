from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import UUIDMixin
from apps.site_config.models import SingletonModel

class Product(UUIDMixin, models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __str__(self):
        return self.name

class Order(UUIDMixin, models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        SHIPPED = 'shipped', _('Shipped')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return f"Order {self.id} by {self.full_name}"

class OrderItem(UUIDMixin, models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')

    def __str__(self):
        return str(self.id)

class EmailTemplate(SingletonModel):
    event_name = models.CharField(max_length=100, unique=True, help_text=_("e.g., 'new_order_admin_notification'"))
    description = models.CharField(max_length=255, blank=True, help_text=_("A short description of when this email is sent."))
    subject = models.CharField(max_length=255)
    body = models.TextField(help_text=_("HTML content. Use placeholders like {{ order.id }} or {{ order.full_name }}."))
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Email Template')
        verbose_name_plural = _('Email Templates')

    def __str__(self):
        return self.event_name 