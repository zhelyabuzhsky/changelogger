from django.contrib import admin

from .models import Project, Version

admin.site.register(Project)
admin.site.register(Version)
