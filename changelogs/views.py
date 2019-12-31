import datetime

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import View
from rest_framework import viewsets

from .models import Project, Version
from .serializers import ProjectSerializer, VersionSerializer
from .services import send_email_notifications


def index(request):
    template = loader.get_template("changelogs/index.html")
    context = {}
    return HttpResponse(template.render(context, request))


def feed(request):
    template = loader.get_template("changelogs/feed.html")

    if request.user.is_authenticated:
        versions = Version.objects.filter(project__subscribers=request.user).all()
    else:
        versions = Version.objects.filter(project__is_public=True).all()

    context = {"versions": versions}
    return HttpResponse(template.render(context, request))


def projects(request):
    template = loader.get_template("changelogs/projects.html")
    if request.user.is_authenticated:
        projects_list = (
            Project.objects.filter(subscribers=request.user).order_by("pk").all()
        )
    else:
        projects_list = Project.objects.filter(is_public=True).order_by("pk").all()

    context = {"projects_list": projects_list}
    return HttpResponse(template.render(context, request))


def api_documentation(request):
    template = loader.get_template("changelogs/api_documentation.html")
    context = {}
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


def profile(request):
    template = loader.get_template("changelogs/profile.html")
    context = {"user": request.user}
    return HttpResponse(template.render(context, request))


def about(request):
    template = loader.get_template("changelogs/about.html")
    context = {}
    return HttpResponse(template.render(context, request))


class AddVersionView(View):
    def get(self, request, project_id: int):
        template = loader.get_template("changelogs/add_version.html")
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            raise Http404("Project does not exist")
        context = {"project": project}
        return HttpResponse(template.render(context, request))

    def post(self, request, project_id: int):
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            raise Http404("Project does not exist")

        version = Version(
            title=request.POST.get("title"),
            date_time=datetime.datetime.now(),
            project=project,
            body=request.POST.get("body"),
        )
        version.save()

        send_email_notifications(version)

        return HttpResponseRedirect(
            reverse("changelogs:project_versions", args=(project.id,))
        )


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
