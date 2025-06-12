from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.urls import reverse
from django.conf import settings

def get_model_metadata(model):
    """
    Extract comprehensive model metadata for frontend rendering and validation.
    """
    fields = {}

    for field in model._meta.get_fields():
        if isinstance(field, (models.ManyToOneRel, models.ManyToManyRel, models.OneToOneRel)):
            # These are reverse relations, we can skip them for direct model fields
            continue

        field_type = field.__class__.__name__
        ui_component = 'textfield' # Default component

        # Determine the UI component based on the field type
        if field_type == 'TextField':
            ui_component = 'textarea'
        elif field_type in ['EmailField', 'URLField']:
            ui_component = field_type.lower().replace('field', '')
        elif field_type in ['ImageField', 'FileField']:
            ui_component = field_type.lower().replace('field', '_upload')
        elif field_type == 'BooleanField':
            ui_component = 'checkbox'
        elif field_type in ['DateField', 'DateTimeField', 'TimeField']:
            ui_component = field_type.lower().replace('field', '_picker')
        elif field.choices:
            ui_component = 'select'
        elif isinstance(field, models.ForeignKey):
            ui_component = 'foreignkey_select'
        elif isinstance(field, models.ManyToManyField):
            ui_component = 'manytomany_select'
        elif field_type == 'ColorField': # Assuming a custom field
             ui_component = 'color_picker'
        elif hasattr(field, 'json_schema'): # For JSONFields with a schema
            ui_component = 'json_editor'


        field_info = {
            'name': field.name,
            'verbose_name': str(field.verbose_name),
            'type': field_type,
            'ui_component': ui_component,
            'required': not field.null and not field.blank,
            'max_length': getattr(field, 'max_length', None),
            'help_text': str(field.help_text) if field.help_text else '',
            'default': field.default if field.default != models.NOT_PROVIDED else None,
            'editable': getattr(field, 'editable', True),
            'is_translation': any(field.name.endswith(f"_{code}") for code, _ in getattr(settings, 'LANGUAGES', [])),
        }

        if hasattr(field, 'choices') and field.choices:
            field_info['choices'] = [
                {'value': choice[0], 'label': str(choice[1])}
                for choice in field.choices
            ]

        if isinstance(field, (models.ForeignKey, models.ManyToManyField, models.OneToOneField)):
            related_model = field.related_model
            try:
                # Construct the API URL for the related model
                related_url = reverse(f'{related_model._meta.model_name}-list')
                api_url = f'/api/admin/models{related_url}'
            except:
                api_url = None # Could not reverse the URL

            field_info['related_model'] = {
                'app_label': related_model._meta.app_label,
                'model_name': related_model._meta.model_name,
                'verbose_name': str(related_model._meta.verbose_name),
                'api_url': api_url
            }

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