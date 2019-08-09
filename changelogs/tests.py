from django.test import TestCase
from django.urls import reverse

from .models import Project


class IndexViewTests(TestCase):
    def test_success(self):
        response = self.client.get(reverse("changelogs:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Collector for your changelogs")


class AllProjectsViewTests(TestCase):
    def test_no_projects(self):
        response = self.client.get(reverse("changelogs:all_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No projects are available.")
        self.assertQuerysetEqual(response.context["all_projects_list"], [])

    def test_success(self):
        Project.objects.create(title="django", url="https://github.com/django/django")
        Project.objects.create(title="requests", url="https://github.com/psf/requests")
        response = self.client.get(reverse("changelogs:all_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "django")
        self.assertContains(response, "https://github.com/django/django")
        self.assertQuerysetEqual(
            response.context["all_projects_list"],
            [
                "<Project: django (https://github.com/django/django)>",
                "<Project: requests (https://github.com/psf/requests)>",
            ],
        )
