from modeltranslation.translator import register, TranslationOptions
from .models import Product, EmailTemplate

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(EmailTemplate)
class EmailTemplateTranslationOptions(TranslationOptions):
    fields = ('description', 'subject', 'body') 