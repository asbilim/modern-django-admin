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
    help = 'Creates multilingual dummy data for the Todo app, including multiple projects and file uploads.'

    def _generate_dummy_image(self):
        """Generates a simple 200x200 PNG image in memory."""
        image_buffer = BytesIO()
        image = Image.new('RGB', (200, 200), color='purple')
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
        
        # --- Create Multiple Projects ---
        projects_data = [
            {'en': "Q3 Marketing Campaign", 'de': "Q3-Marketingkampagne", 'fr': "Campagne marketing T3"},
            {'en': "Website Redesign", 'de': "Neugestaltung der Website", 'fr': "Refonte du site web"},
            {'en': "API Integration for Mobile App", 'de': "API-Integration für mobile App", 'fr': "Intégration de l'API pour l'application mobile"},
        ]
        
        created_projects = []
        self.stdout.write("Creating projects...")
        for p_data in projects_data:
            project = Project(owner=random.choice(users))
            project.name_en, project.name_de, project.name_fr = p_data['en'], p_data['de'], p_data['fr']
            project.description_en = f"Description for {p_data['en']}"
            project.description_de = f"Beschreibung für {p_data['de']}"
            project.description_fr = f"Description pour {p_data['fr']}"
            project.save()
            created_projects.append(project)
            self.stdout.write(f'  - Created project: "{project.name}"')

        # --- Create Multilingual Tasks ---
        tasks_data = [
            {'en': "Draft initial ad copy", 'de': "Ersten Anzeigentext entwerfen", 'fr': "Rédiger le premier texte publicitaire"},
            {'en': "Design new landing page mockups", 'de': "Neue Landing-Page-Mockups entwerfen", 'fr': "Concevoir des maquettes de la nouvelle page d'accueil"},
            {'en': "Develop authentication endpoint", 'de': "Authentifizierungs-Endpunkt entwickeln", 'fr': "Développer le point de terminaison d'authentification"},
            {'en': "Finalize color palette", 'de': "Farbpalette festlegen", 'fr': "Finaliser la palette de couleurs"},
            {'en': "Research competitor APIs", 'de': "Konkurrenz-APIs recherchieren", 'fr': "Rechercher les API des concurrents"},
            {'en': "Set up social media calendar", 'de': "Social-Media-Kalender einrichten", 'fr': "Mettre en place le calendrier des réseaux sociaux"},
            {'en': "Fix login page bug", 'de': "Fehler auf der Anmeldeseite beheben", 'fr': "Corriger le bug de la page de connexion"},
            {'en': "Deploy new feature to staging", 'de': "Neue Funktion in Staging bereitstellen", 'fr': "Déployer la nouvelle fonctionnalité en pré-production"},
            {'en': "Update API documentation", 'de': "API-Dokumentation aktualisieren", 'fr': "Mettre à jour la documentation de l'API"},
        ]

        self.stdout.write(f'Creating {len(tasks_data)} dummy tasks with file uploads...')
        for t_data in tasks_data:
            task = Task(
                project=random.choice(created_projects),
                status=random.choice([choice[0] for choice in Task.Status.choices]),
                assignee=random.choice(users),
                due_date=timezone.now().date() + timedelta(days=random.randint(1, 30)),
                metadata={"priority": random.choice(['low', 'medium', 'high'])}
            )
            task.title_en, task.title_de, task.title_fr = t_data['en'], t_data['de'], t_data['fr']
            task.description_en = f"Detailed description for {t_data['en']}"
            task.description_de = f"Detaillierte Beschreibung für {t_data['de']}"
            task.description_fr = f"Description détaillée pour {t_data['fr']}"
            task.save()

            task.cover_image.save('dummy_cover.png', self._generate_dummy_image())
            task.attachment.save('dummy_attachment.txt', self._generate_dummy_attachment())
            self.stdout.write(f'  - Created task: "{task.title}"')

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(created_projects)} projects and {len(tasks_data)} tasks.')) 