from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.db import models

GITHUB_DOMAIN_NAME = "github.com"


class Project(models.Model):
    class Meta:
        db_table = "projects"
        ordering = ["id"]

    title = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    is_public = models.BooleanField(default=False)
    subscribers = models.ManyToManyField(User, blank=True)

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
