from django.contrib import admin
from .models import EmailSettings, FileStorageSettings

@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    
    class Meta:
        frontend_config = {
            'icon': 'mail',
            'category': 'Site Settings',
            'description': 'Configure system email settings.'
        }

@admin.register(FileStorageSettings)
class FileStorageSettingsAdmin(admin.ModelAdmin):
    
    class Meta:
        frontend_config = {
            'icon': 'folder-open',
            'category': 'Site Settings',
            'description': 'Configure file storage settings (e.g., AWS S3).'
        } 