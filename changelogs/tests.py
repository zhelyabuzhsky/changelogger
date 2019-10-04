from datetime import datetime

from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Project, Version
from .views import projects


class IndexViewTests(TestCase):
    def test_success(self):
        response = self.client.get(reverse("changelogs:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Collector for changelogs")


class ProjectsViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="jacob", email="jacob@mail.com", password="top_secret"
        )

    def tearDown(self):
        self.user.delete()

    def test_no_projects(self):
        response = self.client.get(reverse("changelogs:projects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No projects are available =(")
        self.assertQuerysetEqual(response.context["projects_list"], [])

    def test_anonymous(self):
        Project.objects.create(
            title="django", is_public=True, url="https://github.com/django/django"
        )
        Project.objects.create(
            title="requests", is_public=True, url="https://github.com/psf/requests"
        )
        Project.objects.create(title="flask", url="https://github.com/pallets/flask")
        response = self.client.get(reverse("changelogs:projects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "django")
        self.assertContains(response, "https://github.com/django/django")
        self.assertContains(response, "requests")
        self.assertContains(response, "https://github.com/psf/requests")
        self.assertNotContains(response, "flask")
        self.assertNotContains(response, "https://github.com/pallets/flask")
        self.assertQuerysetEqual(
            response.context["projects_list"],
            [
                "<Project: django (https://github.com/django/django)>",
                "<Project: requests (https://github.com/psf/requests)>",
            ],
        )

    def test_authorized_user(self):
        project_django = Project.objects.create(
            title="django", url="https://github.com/django/django"
        )
        project_django.subscribers.add(self.user)
        Project.objects.create(title="requests", url="https://github.com/psf/requests")
        Project.objects.create(
            title="flask", is_public=True, url="https://github.com/pallets/flask"
        )
        request = self.factory.get(reverse("changelogs:projects"))
        request.user = self.user
        response = projects(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "django")
        self.assertContains(response, "https://github.com/django/django")
        self.assertNotContains(response, "flask")
        self.assertNotContains(response, "https://github.com/pallets/flask")
        self.assertNotContains(response, "requests")
        self.assertNotContains(response, "https://github.com/psf/requests")


class VersionDetailTests(TestCase):
    def test_success(self):
        project_django = Project.objects.create(
            title="django", url="https://github.com/django/django"
        )
        version_django_1 = Version.objects.create(
            title="1.0.0",
            date_time=datetime.now(),
            project=project_django,
            body="* change one* change two",
        )
        response = self.client.get(
            reverse(
                "changelogs:version_detail",
                args=(project_django.id, version_django_1.id),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "django-1.0.0")
        self.assertContains(response, "change one")

    def test_wrong_version(self):
        response = self.client.get(reverse("changelogs:version_detail", args=(1, 1)))
        self.assertEqual(response.status_code, 404)


class ProjectModelTests(TestCase):
    def test_repository_owner_property(self):
        sentry_project = Project.objects.create(
            title="Sentry", url="https://github.com/getsentry/sentry"
        )
        self.assertEqual(sentry_project.repository_owner, "getsentry")

    def test_repository_name_property(self):
        sentry_project = Project.objects.create(
            title="Sentry", url="https://github.com/getsentry/sentry"
        )
        self.assertEqual(sentry_project.repository_name, "sentry")

    def test_is_github_property_true(self):
        sentry_project = Project.objects.create(
            title="Sentry", url="https://github.com/getsentry/sentry"
        )
        self.assertTrue(sentry_project.is_github_project)

    def test_is_github_property_false(self):
        gitlab_project = Project.objects.create(
            title="GitLab", url="https://gitlab.com/gitlab-org/gitlab"
        )
        self.assertFalse(gitlab_project.is_github_project)


class RestApiTests(APITestCase):
    def setUp(self):
        self.group = Group.objects.create(name="Users")
        self.group.permissions.add(Permission.objects.get(name="Can view project"))
        self.group.permissions.add(Permission.objects.get(name="Can view version"))
        self.group.permissions.add(Permission.objects.get(name="Can add version"))
        self.group.permissions.add(Permission.objects.get(name="Can change version"))
        self.group.permissions.add(Permission.objects.get(name="Can delete version"))

        self.user = User.objects.create_user(
            username="jacob", email="jacob@mail.com", password="top_secret"
        )
        self.user.groups.add(self.group)

    def tearDown(self):
        self.user.delete()
        self.group.delete()

    def test_create_new_version_anonymous(self):
        response = self.client.post(
            "/api/versions/",
            {
                "title": "0.1.0",
                "date_time": datetime.now(),
                "body": "small fixes",
                "project": 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_new_version_wrong_permissions(self):
        self.group.permissions.remove(Permission.objects.get(name="Can add version"))

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/versions/",
            {
                "title": "0.1.0",
                "date_time": datetime.now(),
                "body": "small fixes",
                "project": 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_new_version_successful(self):
        sentry_project = Project.objects.create(
            title="Sentry", url="https://github.com/getsentry/sentry"
        )

        self.assertEqual(Version.objects.count(), 0)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/versions/",
            {
                "title": "0.1.0",
                "date_time": datetime.now(),
                "body": "small fixes",
                "project": sentry_project.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Version.objects.count(), 1)
        version = Version.objects.first()
        self.assertEqual(version.project_id, sentry_project.id)
        self.assertEqual(version.body, "small fixes")
