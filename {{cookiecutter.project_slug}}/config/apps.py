from django.apps import AppConfig


class {{ cookiecutter.project_slug.replace('_', ' ').title().replace(' ', '') }}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'config'
