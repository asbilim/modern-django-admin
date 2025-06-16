from django.apps import AppConfig


class AdminApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.admin_api'
    verbose_name = 'Admin API'

    def ready(self):
        from .translation import register_all_translations
        register_all_translations()
