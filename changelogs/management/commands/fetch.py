from django.core.management.base import BaseCommand

from changelogs.models import Project
from changelogs.services import fetch_github_project, fetch_gitlab_project


class Command(BaseCommand):
    help = "Fetches all projects changelogs"

    def handle(self, *args, **options):
        for project in Project.objects.all():
            if project.is_github_project is True:
                fetch_github_project(project)
            else:
                fetch_gitlab_project(project)

        self.stdout.write(self.style.SUCCESS("Successfully fetched changelogs"))
