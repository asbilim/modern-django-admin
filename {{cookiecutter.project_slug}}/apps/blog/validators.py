# apps/blog/validators.py
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_profanity(value):
    """
    A placeholder validator to check for profanity in content.
    This should be replaced with a real implementation.
    """
    # In a real application, you would use a library like 'profanity-check'
    # or a custom list of banned words.
    banned_words = ['profanity', 'badword'] 
    
    if any(word in value.lower() for word in banned_words):
        raise ValidationError(_("Please avoid using inappropriate language."))

def validate_published_date_not_in_future(value):
    """
    Ensures that the publication date is not set in the future.
    This might be useful on a form, but for a 'scheduled' status, future dates are valid.
    I'll leave this here as requested, but it might not be used depending on logic.
    """
    from django.utils import timezone
    if value > timezone.now():
        raise ValidationError(_("Publication date cannot be in the future.")) 