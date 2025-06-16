from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order
from apps.newsletter.models import Subscriber

@receiver(post_save, sender=Order)
def handle_order_updates(sender, instance, created, **kwargs):
    """
    Handles actions after an order is created or updated.
    """
    if created:
        # Notify admin of a new order
        subject = f'New Order Received: #{instance.id}'
        message = f"""
        A new order has been placed.

        Order ID: {instance.id}
        Customer: {instance.first_name} {instance.last_name} ({instance.email})
        Total Amount: ${instance.get_total_cost():.2f}

        Please review the order in the admin panel.
        """
        # Assumes ADMINS setting is configured e.g., ADMINS = [('Admin', 'admin@example.com')]
        admin_emails = [admin[1] for admin in settings.ADMINS]
        if admin_emails:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, admin_emails)

    if instance.status == 'confirmed':
        # Send confirmation email to the customer
        subject = f'Your Order is Confirmed: #{instance.id}'
        message = f"""
        Hi {instance.first_name},

        Your order with ID #{instance.id} has been confirmed.
        We will notify you again once your order has been shipped.

        Thank you for your purchase!
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email])

        # Add the customer to the newsletter subscribers list
        Subscriber.objects.get_or_create(
            email=instance.email,
            defaults={
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'is_active': True,
            }
        ) 