from django.apps import apps
from django.conf import settings
from django.db import models
from modeltranslation.translator import translator, TranslationOptions


def register_all_translations():
    """Automatically register translation fields for all models."""
    local_apps = {app.split('.')[-1] for app in getattr(settings, 'LOCAL_APPS', [])}
    for model in apps.get_models():
        if model._meta.app_label not in local_apps:
            continue
        if model._meta.app_label == 'site_config':
            continue
        if model in translator.get_registered_models():
            continue
        fields = [
            f.name for f in model._meta.get_fields()
            if isinstance(f, (models.CharField, models.TextField))
        ]
        if fields:
            opts = type(
                f"{model.__name__}TranslationOptions",
                (TranslationOptions,),
                {"fields": fields},
            )
            translator.register(model, opts) 