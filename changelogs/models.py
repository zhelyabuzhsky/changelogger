from django.db import models


class Project(models.Model):
    class Meta:
        db_table = 'projects'

    title = models.CharField(max_length=200)
    url = models.URLField(max_length=200)

    def __str__(self):
        return f"{self.title} ({self.url})"
