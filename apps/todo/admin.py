from django.contrib import admin
from .models import Project, Task

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('owner', 'created_at')

    class Meta:
        frontend_config = {
            'icon': 'briefcase',
            'category': 'Task Management',
            'description': 'Group tasks together into projects.'
        }

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assignee', 'status', 'due_date')
    search_fields = ('title', 'description')
    list_filter = ('status', 'due_date', 'assignee', 'project')
    list_editable = ('status', 'assignee', 'due_date')
    
    class Meta:
        frontend_config = {
            'icon': 'check-square',
            'category': 'Task Management',
            'description': 'Manage individual tasks.'
        } 