from modeltranslation.translator import register, TranslationOptions
from .models import Product, ProductCategory

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'content')

@register(ProductCategory)
class ProductCategoryTranslationOptions(TranslationOptions):
    fields = ('name',) 