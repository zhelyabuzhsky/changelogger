from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.urls import reverse

from .models import Project
from .views import my_projects


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
        self.assertContains(response, "requests")
        self.assertContains(response, "https://github.com/psf/requests")
        self.assertQuerysetEqual(
            response.context["all_projects_list"],
            [
                "<Project: django (https://github.com/django/django)>",
                "<Project: requests (https://github.com/psf/requests)>",
            ],
        )


class MyProjectsViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="jacob", email="jacob@mail.com", password="top_secret"
        )

    def test_no_projects(self):
        response = self.client.get(reverse("changelogs:all_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No projects are available.")
        self.assertQuerysetEqual(response.context["all_projects_list"], [])

    def test_success(self):
        project_django = Project.objects.create(
            title="django", url="https://github.com/django/django"
        )
        project_django.subscribers.add(self.user)
        Project.objects.create(title="requests", url="https://github.com/psf/requests")
        request = self.factory.get(reverse("changelogs:my_projects"))
        request.user = self.user
        response = my_projects(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "django")
        self.assertContains(response, "https://github.com/django/django")
        self.assertNotContains(response, "requests")
        self.assertNotContains(response, "https://github.com/psf/requests")
