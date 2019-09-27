from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.template import loader
from rest_framework import viewsets

from .models import Project, Version
from .serializers import ProjectSerializer, VersionSerializer


def index(request):
    123/0
    template = loader.get_template("changelogs/index.html")
    context = {}
    return HttpResponse(template.render(context, request))


def all_projects(request):
    template = loader.get_template("changelogs/all_projects.html")
    all_projects_list = Project.objects.order_by("pk").all()
    context = {"all_projects_list": all_projects_list}
    return HttpResponse(template.render(context, request))


@login_required
def my_projects(request):
    template = loader.get_template("changelogs/my_projects.html")
    my_projects_list = (
        Project.objects.filter(subscribers=request.user).order_by("pk").all()
    )
    context = {"my_projects_list": my_projects_list}
    return HttpResponse(template.render(context, request))


def feed(request):
    template = loader.get_template("changelogs/feed.html")

    if request.user.is_authenticated:
        versions = (
            Version.objects.filter(project__subscribers=request.user)
            .order_by("date_time")
            .all()
        )
    else:
        versions = (
            Version.objects.filter(project__is_public=True).order_by("date_time").all()
        )

    context = {"versions": versions}
    return HttpResponse(template.render(context, request))


def project_detail(request, project_id: int):
    template = loader.get_template("changelogs/project_detail.html")
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    context = {"project": project}
    return HttpResponse(template.render(context, request))


def project_versions(request, project_id: int):
    template = loader.get_template("changelogs/project_versions.html")
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    context = {"project": project}
    return HttpResponse(template.render(context, request))


def version_detail(request, project_id: int, version_id: int):
    template = loader.get_template("changelogs/version_detail.html")
    try:
        version = Version.objects.filter(project_id=project_id).get(pk=version_id)
    except Version.DoesNotExist:
        raise Http404("Version does not exist")
    context = {"version": version}
    return HttpResponse(template.render(context, request))


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class VersionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows versions to be viewed or edited.
    """

    queryset = Version.objects.all()
    serializer_class = VersionSerializer
