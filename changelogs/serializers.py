from rest_framework import serializers

from .models import Project, Version


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "title", "url"]


class VersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Version
        fields = ["id", "title", "date_time", "body", "project_id"]
