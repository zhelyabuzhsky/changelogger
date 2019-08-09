from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    class Meta:
        db_table = "projects"

    title = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    subscribers = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return f"{self.title} ({self.url})"
