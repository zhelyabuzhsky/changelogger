from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Project, User, Version

admin.site.register(Project)
admin.site.register(Version)
admin.site.register(User, UserAdmin)
