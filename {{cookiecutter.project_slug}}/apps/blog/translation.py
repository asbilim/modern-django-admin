from modeltranslation.translator import register, TranslationOptions
from .models import Post
from apps.core.models import Category

@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'excerpt', 'slug', 'meta_title', 'meta_description', 'meta_keywords')

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'slug', 'meta_title', 'meta_description') 