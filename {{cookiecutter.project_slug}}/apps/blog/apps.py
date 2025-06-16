from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.blog'
    verbose_name = 'Blog'
    
    def ready(self):
        # This is where you connect your signals
        import apps.blog.signals
        # This is also where you can import your translation options
        import apps.blog.translation

        # Import translation module 