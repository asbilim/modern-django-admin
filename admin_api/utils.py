from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin

def get_model_metadata(model):
    """Extract comprehensive model metadata for frontend"""
    fields = {}
    
    for field in model._meta.fields:
        field_info = {
            'name': field.name,
            'verbose_name': str(field.verbose_name),
            'type': field.__class__.__name__,
            'required': not field.null and not field.blank,
            'max_length': getattr(field, 'max_length', None),
            'help_text': str(field.help_text) if field.help_text else '',
            'default': field.default if field.default != models.NOT_PROVIDED else None,
            'editable': field.editable,
        }
        
        # Handle choices
        if hasattr(field, 'choices') and field.choices:
            field_info['choices'] = [
                {'value': choice[0], 'label': str(choice[1])}
                for choice in field.choices
            ]
        
        # Handle relationships
        if isinstance(field, models.ForeignKey):
            field_info['related_model'] = {
                'app_label': field.related_model._meta.app_label,
                'model_name': field.related_model._meta.model_name,
                'verbose_name': str(field.related_model._meta.verbose_name),
            }
        
        # Handle special field types
        if isinstance(field, models.DateTimeField):
            field_info['auto_now'] = getattr(field, 'auto_now', False)
            field_info['auto_now_add'] = getattr(field, 'auto_now_add', False)
        
        fields[field.name] = field_info
    
    return fields

def get_admin_site_config():
    """Get configuration for the entire admin site"""
    models_config = {}
    categories = {}
    
    for model, model_admin in admin.site._registry.items():
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        
        # Get frontend config
        frontend_config = {}
        if hasattr(model_admin, 'Meta') and hasattr(model_admin.Meta, 'frontend_config'):
            frontend_config = model_admin.Meta.frontend_config
        
        category = frontend_config.get('category', 'Other')
        
        models_config[f'{app_label}.{model_name}'] = {
            'app_label': app_label,
            'model_name': model_name,
            'verbose_name': str(model._meta.verbose_name),
            'verbose_name_plural': str(model._meta.verbose_name_plural),
            'category': category,
            'frontend_config': frontend_config
        }
        
        # Group by category
        if category not in categories:
            categories[category] = []
        categories[category].append(f'{app_label}.{model_name}')
    
    return {
        'models': models_config,
        'categories': categories
    } 