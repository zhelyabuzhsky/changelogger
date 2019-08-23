from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    class Meta:
        db_table = "projects"

    title = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    subscribers = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return f"{self.title} ({self.url})"


class Version(models.Model):
    class Meta:
        db_table = "versions"

    title = models.CharField(max_length=20)
    date_time = models.DateTimeField()
    body = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} ({self.project.title})"
