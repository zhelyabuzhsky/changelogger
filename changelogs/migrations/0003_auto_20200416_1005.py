# Generated by Django 3.0.3 on 2020-04-16 10:05

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("changelogs", "0002_user_github_token"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="subscribers",
            field=models.ManyToManyField(
                blank=True, related_name="subscribers", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
