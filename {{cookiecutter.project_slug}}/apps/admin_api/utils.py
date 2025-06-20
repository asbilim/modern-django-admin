from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.urls import reverse, NoReverseMatch
from django.conf import settings
from modeltranslation.translator import translator, NotRegistered

def get_model_metadata(model, model_admin=None):
    """
    Extract comprehensive model metadata for frontend rendering and validation.
    """
    fields = {}
    field_metadata_config = {}
    if model_admin and hasattr(model_admin, 'Meta') and hasattr(model_admin.Meta, 'field_metadata'):
        field_metadata_config = model_admin.Meta.field_metadata

    try:
        trans_opts = translator.get_options_for_model(model)
        translated_field_names = trans_opts.fields
    except NotRegistered:
        trans_opts = None
        translated_field_names = []

    for field in model._meta.get_fields():
        if isinstance(field, (models.ManyToOneRel, models.ManyToManyRel, models.OneToOneRel)):
            # These are reverse relations, we can skip them for direct model fields
            continue

        # If this is an original field that has translations, skip it.
        # We'll process its language-specific variants instead.
        if field.name in translated_field_names:
            continue

        field_type = field.__class__.__name__
        
        # Start with a default component
        ui_component = 'textfield'

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

        is_translated_field = False
        base_field_name = field.name

        if trans_opts:
            for lang_code, _ in getattr(settings, 'LANGUAGES', []):
                {% raw %}suffix = f'_{lang_code}'{% endraw %}
                if field.name.endswith(suffix):
                    possible_base_name = field.name[:-len(suffix)]
                    if possible_base_name in translated_field_names:
                        is_translated_field = True
                        base_field_name = possible_base_name
                        break
        
        # Check for overrides from the admin class using the base field name
        if base_field_name in field_metadata_config:
            ui_component = field_metadata_config[base_field_name].get('ui_component', ui_component)

        field_info = {
            'name': field.name,
            'verbose_name': str(field.verbose_name),
            'type': field_type,
            'ui_component': ui_component,
            'required': not field.null and not field.blank,
            'max_length': getattr(field, 'max_length', None),
            'help_text': str(field.help_text) if field.help_text else '',
            'editable': getattr(field, 'editable', True),
            'is_translation': is_translated_field,
        }

        # Handle default value - ensure it's JSON serializable
        if field.default != models.NOT_PROVIDED:
            if callable(field.default):
                # If default is a callable, just indicate it has a default function
                field_info['default'] = "Function default"
            else:
                # Make sure the default value is serializable
                try:
                    # Test if it can be serialized
                    import json
                    json.dumps(field.default)
                    field_info['default'] = field.default
                except (TypeError, OverflowError):
                    # If not serializable, convert to string representation
                    field_info['default'] = str(field.default)
        else:
            field_info['default'] = None

        if hasattr(field, 'choices') and field.choices:
            field_info['choices'] = [
                {'value': choice[0], 'label': str(choice[1])}
                for choice in field.choices
            ]

        if isinstance(field, (models.ForeignKey, models.ManyToManyField, models.OneToOneField)):
            related_model = field.related_model
            try:
                # Construct the API URL for the related model
                {% raw %}api_url = reverse(f'admin_api:{related_model._meta.model_name}-list'){% endraw %}
            except NoReverseMatch:
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
        
        try:
            # Construct the API URL for the model list view.
            # The router registers routes with names like '<model_name>-list'.
            {% raw %}list_url = reverse(f'admin_api:{model_name}-list'){% endraw %}
            # The full path is composed of the router's prefix and the reversed URL.
            api_url = list_url
        except NoReverseMatch:
            # This might fail if a model is registered with the admin
            # but not exposed via the API generator for some reason.
            api_url = None
            
        {% raw %}models_config[f'{app_label}.{model_name}'] = {
            'app_label': app_label,
            'model_name': model_name,
            'verbose_name': str(model._meta.verbose_name),
            'verbose_name_plural': str(model._meta.verbose_name_plural),
            'category': category,
            'frontend_config': frontend_config,
            'api_url': api_url,
        }{% endraw %}
        
        # Group by category
        if category not in categories:
            categories[category] = []
        {% raw %}categories[category].append(f'{app_label}.{model_name}'){% endraw %}
    
    # Define comprehensive icon choices for the frontend to use.
    frontend_options = {
        'languages': settings.LANGUAGES,
        'categories': [
            'Access Control',
            'Task Management',
            'Content',
            'Configuration',
            'Site Settings',
            'Other',
        ],
        'icons': [
            # User & Access Control
            'user', 'users', 'user-plus', 'user-minus', 'user-check', 'user-x',
            'shield', 'shield-check', 'lock', 'unlock', 'key', 'fingerprint',
            
            # Business & Work
            'briefcase', 'building', 'office-building', 'home', 'map-pin',
            'phone', 'smartphone', 'tablet', 'laptop', 'monitor',
            
            # Tasks & Projects
            'check-square', 'square', 'list', 'check-circle', 'circle',
            'clipboard', 'clipboard-check', 'clipboard-list', 'target',
            'flag', 'bookmark', 'star', 'heart', 'thumbs-up', 'thumbs-down',
            
            # Content & Media
            'folder', 'folder-open', 'folder-plus', 'file', 'file-text',
            'image', 'video', 'music', 'headphones', 'camera', 'film',
            'book', 'book-open', 'newspaper', 'pen-tool', 'edit', 'edit-3',
            
            # Communication & Social
            'mail', 'message-square', 'message-circle', 'phone-call',
            'send', 'share', 'share-2', 'link', 'link-2', 'external-link',
            
            # Navigation & Organization
            'tag', 'tags', 'hash', 'menu', 'more-horizontal', 'more-vertical',
            'grid', 'list', 'sidebar', 'layout', 'columns', 'rows',
            
            # System & Settings
            'settings', 'cog', 'tool', 'wrench', 'sliders', 'toggle-left',
            'toggle-right', 'power', 'refresh-cw', 'download', 'upload',
            'database', 'server', 'cloud', 'wifi', 'globe', 'compass',
            
            # Analytics & Reports
            'bar-chart', 'bar-chart-2', 'pie-chart', 'trending-up', 'trending-down',
            'activity', 'pulse', 'eye', 'search', 'filter', 'sort-asc', 'sort-desc',
            
            # Status & Alerts
            'info', 'help-circle', 'alert-circle', 'alert-triangle', 'x-circle',
            'check-circle', 'clock', 'calendar', 'bell', 'bell-off',
            
            # Actions & Controls
            'plus', 'plus-circle', 'minus', 'minus-circle', 'x', 'trash',
            'trash-2', 'archive', 'save', 'copy', 'scissors', 'rotate-cw',
            'rotate-ccw', 'maximize', 'minimize', 'zoom-in', 'zoom-out',
            
            # Commerce & Finance
            'shopping-cart', 'shopping-bag', 'credit-card', 'dollar-sign',
            'percent', 'gift', 'award', 'package', 'truck', 'map',
            
            # Time & Scheduling
            'calendar', 'clock', 'watch', 'timer', 'stopwatch', 'sunrise',
            'sunset', 'moon', 'sun', 'zap', 'battery', 'battery-charging',
            
            # Additional Utility Icons
            'anchor', 'aperture', 'box', 'droplet', 'feather', 'layers',
            'paperclip', 'printer', 'rss', 'terminal', 'type', 'umbrella',
            'wind', 'zap-off', 'cpu', 'hard-drive', 'radio', 'bluetooth'
        ]
    }

    return {
        'models': models_config,
        'categories': categories,
        'frontend_options': frontend_options,
    }