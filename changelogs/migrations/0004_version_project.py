# Generated by Django 2.2.4 on 2019-08-23 10:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('changelogs', '0003_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='version',
            name='project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='changelogs.Project'),
            preserve_default=False,
        ),
    ]
