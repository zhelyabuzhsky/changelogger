import datetime

import django.db.models.deletion
import pytz
from django.contrib.auth.models import Group, Permission
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from changelogs.models import Project, User, Version


class IndexViewTests(TestCase):
    def test_successful(self):
        response = self.client.get(reverse("changelogs:index"))
        self.assertContains(response, "Collector for changelogs")


class AboutViewTests(TestCase):
    def test_successful(self):
        response = self.client.get(reverse("changelogs:about"))
        self.assertContains(
            response, "Changelogger is a service to store all your changelogs"
        )


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jacob",
            email="jacob@mail.com",
            password="top_secret",
            first_name="Jacob",
            last_name="Smith",
        )

    def test_anonymous(self):
        response = self.client.get(reverse("changelogs:profile"))
        self.assertRedirects(response, "/login/?next=/profile/")

    def test_successful(self):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.get(reverse("changelogs:profile"))
        self.assertContains(response, "name: Jacob Smith")
        self.assertContains(response, "e-mail: jacob@mail.com")
        self.assertContains(response, f"API token: {self.user.auth_token}")


class SubscriptionsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jacob", email="jacob@mail.com", password="top_secret"
        )

    def test_successful(self):
        another_user = User.objects.create_user(
            username="john", email="john@mail.com", password="my_password"
        )
        Project.objects.create(
            title="django",
            is_public=True,
            url="https://github.com/django/django",
            owner=self.user,
        )
        Project.objects.create(
            title="requests", url="https://github.com/psf/requests", owner=another_user,
        )
        self.client.login(username="jacob", password="top_secret")
        response = self.client.get(reverse("changelogs:subscriptions"))
        self.assertContains(response, "Manage subscriptions")
        self.assertContains(response, "django")
        self.assertNotContains(response, "requests")

    def test_anonymous(self):
        response = self.client.get(reverse("changelogs:subscriptions"))
        self.assertRedirects(response, "/login/?next=/subscriptions/")


class ApiDocumentationViewTests(TestCase):
    def test_successful(self):
        response = self.client.get(reverse("changelogs:api_documentation"))
        self.assertContains(response, "Automate Changelogger via a simple API.")


class ProjectsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jacob", email="jacob@mail.com", password="top_secret"
        )

    def test_no_projects(self):
        response = self.client.get(reverse("changelogs:projects"))
        self.assertContains(response, "No projects are available =(")
        self.assertQuerysetEqual(response.context["projects_list"], [])

    def test_anonymous(self):
        Project.objects.create(
            title="django",
            is_public=True,
            url="https://github.com/django/django",
            owner=self.user,
        )
        Project.objects.create(
            title="requests",
            is_public=True,
            url="https://github.com/psf/requests",
            owner=self.user,
        )
        Project.objects.create(
            title="flask", url="https://github.com/pallets/flask", owner=self.user
        )
        response = self.client.get(reverse("changelogs:projects"))
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
            title="django", url="https://github.com/django/django", owner=self.user
        )
        project_django.subscribers.add(self.user)
        Project.objects.create(
            title="requests", url="https://github.com/psf/requests", owner=self.user
        )
        Project.objects.create(
            title="flask",
            is_public=True,
            url="https://github.com/pallets/flask",
            owner=self.user,
        )
        self.client.login(username="jacob", password="top_secret")
        response = self.client.get(reverse("changelogs:projects"))
        self.assertContains(response, "django")
        self.assertContains(response, "https://github.com/django/django")
        self.assertNotContains(response, "flask")
        self.assertNotContains(response, "https://github.com/pallets/flask")
        self.assertNotContains(response, "requests")
        self.assertNotContains(response, "https://github.com/psf/requests")


class VersionDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jacob", email="jacob@mail.com", password="top_secret"
        )

    def test_successful(self):
        project_django = Project.objects.create(
            title="django", url="https://github.com/django/django", owner=self.user
        )
        version_django_1 = Version.objects.create(
            title="1.0.0",
            date_time=datetime.datetime.now(tz=pytz.utc),
            project=project_django,
            body=(
                "* change one",
                "* change two",
                "![image](/uploads/c76c7e2525ac077aea6334e1f87c88b1/image.png)",
            ),
        )
        self.client.login(username="jacob", password="top_secret")
        response = self.client.get(
            reverse(
                "changelogs:version_detail",
                args=(project_django.id, version_django_1.id),
            )
        )
        self.assertContains(response, "django-1.0.0")
        self.assertContains(response, "change one")
        self.assertContains(
            response,
            """
            <img
                alt="image"
                src="https://github.com/django/django/uploads/c76c7e2525ac077aea6334e1f87c88b1/image.png"
            />
            """,
            html=True,
        )

    def test_wrong_version(self):
        response = self.client.get(reverse("changelogs:version_detail", args=(1, 1)))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_wrong_permissions(self):
        project_django = Project.objects.create(
            title="django",
            url="https://github.com/django/django",
            owner=self.user,
            is_public=False,
        )
        versions_django_1 = Version.objects.create(
            title="1.0.0",
            date_time=datetime.datetime.now(tz=pytz.utc),
            project=project_django,
            body="* change one* change two",
        )
        response = self.client.get(
            reverse(
                "changelogs:version_detail",
                args=(project_django.id, versions_django_1.id,),
            )
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProjectDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jacob", email="jacob@mail.com", password="top_secret"
        )

    def test_logged_in_successful(self):
        project_django = Project.objects.create(
            title="django",
            url="https://github.com/django/django",
            owner=self.user,
            is_public=False,
        )
        Version.objects.create(
            title="1.0.0",
            date_time=datetime.datetime.now(tz=pytz.utc),
            project=project_django,
            body="* change one* change two",
        )

        self.client.login(username="jacob", password="top_secret")
        response = self.client.get(
            reverse("changelogs:project_detail", args=(project_django.id,),)
        )
        self.assertContains(response, "django")

    def test_logged_in_wrong_permissions(self):
        another_user = User.objects.create_user(
            username="john", email="john@mail.com", password="my_password"
        )
        project_django = Project.objects.create(
            title="django",
            url="https://github.com/django/django",
            owner=another_user,
            is_public=False,
        )
        Version.objects.create(
            title="1.0.0",
            date_time=datetime.datetime.now(tz=pytz.utc),
            project=project_django,
            body="* change one* change two",
        )

        self.client.login(username="jacob", password="top_secret")
        response = self.client.get(
            reverse("changelogs:project_detail", args=(project_django.id,),)
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_successful(self):
        project_django = Project.objects.create(
            title="django",
            url="https://github.com/django/django",
            owner=self.user,
            is_public=True,
        )
        Version.objects.create(
            title="1.0.0",
            date_time=datetime.datetime.now(tz=pytz.utc),
            project=project_django,
            body="* change one* change two",
        )
        response = self.client.get(
            reverse("changelogs:project_detail", args=(project_django.id,),)
        )
        self.assertContains(response, "django")

    def test_anonymous_wrong_permissions(self):
        project_django = Project.objects.create(
            title="django",
            url="https://github.com/django/django",
            owner=self.user,
            is_public=False,
        )
        response = self.client.get(
            reverse("changelogs:project_detail", args=(project_django.id,),)
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AddVersionViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jacob", email="jacob@mail.com", password="top_secret"
        )

    def test_get_successful(self):
        self.client.login(username="jacob", password="top_secret")
        project_django = Project.objects.create(
            title="Django", url="https://github.com/django/django", owner=self.user
        )
        response = self.client.get(
            reverse("changelogs:add_version", args=(project_django.id,),)
        )
        self.assertContains(response, "Title")
        self.assertContains(response, "Body")
        self.assertContains(response, "Add version to Django")

    def test_get_anonymous(self):
        response = self.client.get(reverse("changelogs:add_version", args=(1000,),))
        self.assertRedirects(response, "/login/?next=/projects/1000/versions/add")

    def test_get_wrong_project_id(self):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.get(reverse("changelogs:add_version", args=(1000,),))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProjectModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jacob", email="jacob@mail.com", password="top_secret"
        )

    def test_repository_owner_property(self):
        sentry_project = Project.objects.create(
            title="Sentry", url="https://github.com/getsentry/sentry", owner=self.user
        )
        self.assertEqual(sentry_project.repository_owner, "getsentry")

    def test_repository_name_property(self):
        sentry_project = Project.objects.create(
            title="Sentry", url="https://github.com/getsentry/sentry", owner=self.user
        )
        self.assertEqual(sentry_project.repository_name, "sentry")

    def test_is_github_property_true(self):
        sentry_project = Project.objects.create(
            title="Sentry", url="https://github.com/getsentry/sentry", owner=self.user
        )
        self.assertTrue(sentry_project.is_github_project)

    def test_is_github_property_false(self):
        gitlab_project = Project.objects.create(
            title="GitLab", url="https://gitlab.com/gitlab-org/gitlab", owner=self.user
        )
        self.assertFalse(gitlab_project.is_github_project)

    def test_str_representation(self):
        sentry_project = Project.objects.create(
            title="Sentry", url="https://github.com/getsentry/sentry", owner=self.user
        )
        self.assertEqual(
            str(sentry_project), "Sentry (https://github.com/getsentry/sentry)"
        )

    def test_project_owner_delete(self):
        Project.objects.create(
            title="Sentry", url="https://github.com/getsentry/sentry", owner=self.user
        )
        with self.assertRaises(django.db.models.deletion.ProtectedError):
            self.user.delete()

    def test_accessible_by_user_filter(self):
        user = User.objects.create_user(
            username="sherlock", email="sherlock@mail.com", password="top_secret"
        )
        another_user = User.objects.create_user(
            username="john", email="john@mail.com", password="my_password"
        )
        project_1 = Project.objects.create(
            title="Project1", url="https://github.com/me/project1", owner=user
        )
        project_1.team.add(user)
        project_1.team.add(another_user)
        project_2 = Project.objects.create(
            title="Project2", url="https://github.com/me/project2", owner=another_user
        )
        project_3 = Project.objects.create(
            title="Project3",
            url="https://github.com/me/project3",
            owner=user,
            is_public=True,
        )
        project_4 = Project.objects.create(
            title="Project4",
            url="https://github.com/me/project4",
            owner=another_user,
            is_public=True,
        )

        projects = Project.objects.accessible_by_user(user).all()
        self.assertEqual(len(projects), 3)
        self.assertTrue(project_1 in projects)
        self.assertTrue(project_2 not in projects)
        self.assertTrue(project_3 in projects)
        self.assertTrue(project_4 in projects)


class VersionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jacob", email="jacob@mail.com", password="top_secret"
        )

    def test_str_representation(self):
        sentry_project = Project.objects.create(
            title="Sentry", url="https://github.com/getsentry/sentry", owner=self.user
        )
        version_sentry_1 = Version.objects.create(
            title="1.0.0",
            date_time=datetime.datetime.now(tz=pytz.utc),
            project=sentry_project,
            body="* change one* change two",
        )
        self.assertEqual(str(version_sentry_1), "1.0.0 (Sentry)")


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

    def test_create_new_version_anonymous(self):
        response = self.client.post(
            "/api/versions/",
            {
                "title": "0.1.0",
                "date_time": datetime.datetime.now(tz=pytz.utc),
                "body": "small fixes",
                "project": 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_new_version_wrong_permissions(self):
        self.group.permissions.remove(Permission.objects.get(name="Can add version"))

        self.client.force_authenticate(user=self.user, token=self.user.auth_token)

        response = self.client.post(
            "/api/versions/",
            {
                "title": "0.1.0",
                "date_time": datetime.datetime.now(tz=pytz.utc),
                "body": "small fixes",
                "project": 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_new_version_successful(self):
        sentry_project = Project.objects.create(
            title="Sentry", url="https://github.com/getsentry/sentry", owner=self.user
        )

        self.assertEqual(Version.objects.count(), 0)

        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.post(
            "/api/versions/",
            {
                "title": "0.1.0",
                "date_time": datetime.datetime.now(tz=pytz.utc),
                "body": "small fixes",
                "project": sentry_project.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Version.objects.count(), 1)
        version = Version.objects.first()
        self.assertEqual(version.project_id, sentry_project.id)
        self.assertEqual(version.body, "small fixes")

    def test_view_version_successful(self):
        project_django = Project.objects.create(
            title="django", url="https://github.com/django/django", owner=self.user
        )
        project_django.subscribers.add(self.user)
        version_django_1 = Version.objects.create(
            title="1.0.0",
            date_time=datetime.datetime(2019, 12, 4, tzinfo=pytz.utc),
            project=project_django,
            body="* change one* change two",
        )
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(f"/api/versions/{version_django_1.id}/")
        self.assertEqual(
            response.json(),
            {
                "body": "* change one* change two",
                "date_time": "2019-12-04T00:00:00Z",
                "id": 1,
                "project": 1,
                "title": "1.0.0",
            },
        )

    def test_view_project_successful(self):
        project_django = Project.objects.create(
            title="django", url="https://github.com/django/django", owner=self.user
        )
        self.client.force_authenticate(user=self.user, token=self.user.auth_token)
        response = self.client.get(f"/api/projects/{project_django.id}/")
        self.assertEqual(
            response.json(),
            {"id": 1, "title": "django", "url": "https://github.com/django/django"},
        )


class AddProjectViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jacob", email="jacob@mail.com", password="top_secret"
        )

    def test_get_successful(self):
        self.client.login(username="jacob", password="top_secret")
        response = self.client.get(reverse("changelogs:add_project"))
        self.assertContains(response, "Title")
        self.assertContains(response, "URL")
        self.assertContains(response, "Is public")
        self.assertContains(response, "Add project")

    def test_post_successful(self):
        self.assertEqual(Project.objects.count(), 0)
        self.client.login(username="jacob", password="top_secret")
        response = self.client.post(
            reverse("changelogs:add_project"),
            {"title": "Django", "url": "https://github.com/django/django"},
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        project = Project.objects.first()
        self.assertEqual(project.title, "Django")
        self.assertEqual(project.url, "https://github.com/django/django")
        self.assertFalse(project.is_public)
        self.assertEqual(project.owner, self.user)

    def test_anonymous(self):
        response = self.client.get(reverse("changelogs:add_project"))
        self.assertRedirects(response, "/login/?next=/projects/add")


class CustomErrorHandlerTests(SimpleTestCase):
    def test_handler_renders_template_response(self):
        response = self.client.get("/404/")
        self.assertContains(
            response, "Page not found =(", status_code=status.HTTP_404_NOT_FOUND
        )
