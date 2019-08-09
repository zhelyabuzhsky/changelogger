from django.http import HttpResponse
from django.template import loader
from rest_framework import viewsets
from .models import Project
from .serializers import ProjectSerializer


def index(request):
    template = loader.get_template("changelogs/index.html")
    context = {}
    return HttpResponse(template.render(context, request))


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
