from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template import Template, Context
from django.conf import settings
from .models import Order, EmailTemplate
from apps.site_identity.models import SiteIdentity

@receiver(post_save, sender=Order)
def send_new_order_email(sender, instance, created, **kwargs):
    if created:
        try:
            # Get the email template
            template_model = EmailTemplate.objects.get(event_name='new_order_admin_notification', is_active=True)
            
            # Get site identity for admin email
            site_identity = SiteIdentity.load()
            admin_email = site_identity.contact_email
            
            if not admin_email:
                # Fallback to default from email or admin setting
                admin_email = settings.DEFAULT_FROM_EMAIL or [admin[1] for admin in settings.ADMINS]
            
            if admin_email:
                # Prepare context for the template
                context_data = {
                    'order': instance,
                    'items': instance.items.all(),
                    'site_name': site_identity.name
                }
                context = Context(context_data)
                
                # Render subject and body
                subject_template = Template(template_model.subject)
                body_template = Template(template_model.body)
                
                subject = subject_template.render(context)
                body = body_template.render(context)
                
                send_mail(
                    subject=subject,
                    message=body, # this is a fallback for email clients that don't support HTML
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin_email],
                    html_message=body,
                    fail_silently=False,
                )
        except EmailTemplate.DoesNotExist:
            # Handle case where template is not found
            print(f"Email template 'new_order_admin_notification' not found. Cannot send email for Order {instance.id}.")
        except Exception as e:
            # Log any other exception
            print(f"Error sending new order email for Order {instance.id}: {e}") 