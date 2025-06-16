from django.db import models
from django.contrib.auth.models import User
from apps.core.models import Tag

class Project(models.Model):
    """A project to group tasks."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    """A single task item."""
    class Status(models.TextChoices):
        TODO = 'todo', 'To Do'
        IN_PROGRESS = 'in_progress', 'In Progress'
        DONE = 'done', 'Done'
        ARCHIVED = 'archived', 'Archived'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text="A full description of the task.")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    due_date = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    # Complex Fields for Testing
    attachment = models.FileField(upload_to='task_attachments/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='task_covers/', blank=True, null=True)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='JSON metadata for the task (e.g., {"priority": "high", "effort_hours": 2})'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title 