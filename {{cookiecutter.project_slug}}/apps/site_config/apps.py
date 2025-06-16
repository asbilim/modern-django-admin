from django.apps import AppConfig

class SiteConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.site_config'
    verbose_name = 'Site Configuration'

    def ready(self):
        import apps.site_config.signals 