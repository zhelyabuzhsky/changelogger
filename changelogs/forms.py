from django.forms import (
    CheckboxInput,
    ModelForm,
    TextInput,
    Textarea,
    URLInput,
    EmailInput,
)

from .models import Project, Version, User


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "gitlab_token",
        ]
        widgets = {
            "first_name": TextInput(attrs={"class": "form-control"}),
            "last_name": TextInput(attrs={"class": "form-control"}),
            "email": EmailInput(attrs={"class": "form-control"}),
            "gitlab_token": TextInput(attrs={"class": "form-control"}),
        }


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["title", "url", "is_public"]
        widgets = {
            "title": TextInput(attrs={"class": "form-control"}),
            "url": URLInput(attrs={"class": "form-control"}),
            "is_public": CheckboxInput(attrs={"class": "form-check-input"}),
        }


class VersionForm(ModelForm):
    class Meta:
        model = Version
        fields = ["title", "body"]
        widgets = {
            "title": TextInput(attrs={"class": "form-control"}),
            "body": Textarea(attrs={"class": "form-control"}),
        }
