import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.todo.models import Project, Task
from datetime import timedelta
from django.utils import timezone
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

class Command(BaseCommand):
    help = 'Creates dummy data for the Todo app, including uploading sample files.'

    def _generate_dummy_image(self):
        """Generates a simple 200x200 PNG image in memory."""
        image_buffer = BytesIO()
        image = Image.new('RGB', (200, 200), color='blue')
        image.save(image_buffer, format='PNG')
        return ContentFile(image_buffer.getvalue(), name='dummy_cover.png')

    def _generate_dummy_attachment(self):
        """Generates a simple text file in memory."""
        text_content = b"This is a dummy attachment file for testing purposes."
        return ContentFile(text_content, name='dummy_attachment.txt')

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old Tasks and Projects...')
        # Note: Deleting objects will not automatically delete files from R2/S3.
        # This is standard behavior to prevent accidental data loss.
        Task.objects.all().delete()
        Project.objects.all().delete()

        self.stdout.write('Creating new dummy data...')
        
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.ERROR('No superuser found. Please create one with `python manage.py createsuperuser`'))
            return

        users = list(User.objects.all())
        owner = users[0]

        project = Project.objects.create(
            name="Alpha Project",
            description="A sample project to house the dummy tasks for testing and demonstration.",
            owner=owner
        )
        self.stdout.write(self.style.SUCCESS(f'Successfully created project: {project.name}'))

        titles = [
            "Finalize Q2 report", "Prepare presentation for Monday", "Fix login page bug",
            "Deploy new feature to production", "Onboard new marketing team member",
            "Brainstorm ideas for the new campaign", "Review pull request #123",
            "Update documentation for the API", "Schedule team-building event",
            "Research competitor pricing models"
        ]

        self.stdout.write(f'Creating {len(titles)} dummy tasks with file uploads...')
        for title in titles:
            task = Task(
                project=project,
                title=title,
                description=f"This is a detailed description for the task: {title}.",
                status=random.choice([choice[0] for choice in Task.Status.choices]),
                assignee=random.choice(users),
                due_date=timezone.now().date() + timedelta(days=random.randint(1, 30)),
                metadata={"priority": random.choice(['low', 'medium', 'high'])}
            )
            
            # Attach generated files
            task.cover_image.save('dummy_cover.png', self._generate_dummy_image())
            task.attachment.save('dummy_attachment.txt', self._generate_dummy_attachment())

            # The task is saved implicitly by the .save() on the FileField
            self.stdout.write(f'  - Created task: "{title}"')

        self.stdout.write(self.style.SUCCESS(f'Successfully created and uploaded files for {len(titles)} dummy tasks.')) 