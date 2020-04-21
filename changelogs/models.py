from urllib.parse import urlparse

import markdown as md
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

from changelogs.validators import validate_project_url

GITHUB_DOMAIN_NAME = "github.com"


class User(AbstractUser):
    gitlab_token = models.CharField(max_length=20, blank=True)
    github_token = models.CharField(max_length=40, blank=True)


class ProjectQuerySet(models.QuerySet):
    def accessible_by_user(self, user):
        return self.filter(Q(team=user) | Q(owner=user) | Q(is_public=True)).distinct()


class Project(models.Model):
    class Meta:
        db_table = "projects"
        ordering = ["id"]

    title = models.CharField(max_length=50)
    url = models.URLField(max_length=100, validators=[validate_project_url])
    is_public = models.BooleanField(default=False)
    subscribers = models.ManyToManyField(User, blank=True, related_name="subscribers")
    owner = models.ForeignKey(
        User, default=None, null=False, on_delete=models.PROTECT, related_name="owner"
    )
    team = models.ManyToManyField(User, blank=True, related_name="team")

    def is_subscribed_by_user(self, user: User) -> bool:
        return user in self.subscribers.all()

    @property
    def repository_owner(self) -> str:
        return urlparse(self.url).path.split("/")[1]

    @property
    def repository_name(self) -> str:
        return urlparse(self.url).path.split("/")[2]

    @property
    def versions(self):
        return Version.objects.filter(project=self)

    @property
    def is_github_project(self) -> bool:
        return urlparse(self.url).netloc == GITHUB_DOMAIN_NAME

    def __str__(self):
        return f"{self.title} ({self.url})"

    objects = ProjectQuerySet.as_manager()


class Version(models.Model):
    class Meta:
        db_table = "versions"
        ordering = ["-date_time"]

    title = models.CharField(max_length=20)
    date_time = models.DateTimeField()
    body = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} ({self.project.title})"

    @property
    def body_html(self):
        body = self.body.replace("![image](/", f"![image]({self.project.url}/")
        return md.markdown(body, extensions=["markdown.extensions.fenced_code"])
