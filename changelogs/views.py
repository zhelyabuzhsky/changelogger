import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse
from django.views import View
from rest_framework import viewsets

from changelogs.forms import ProjectForm, UserForm, VersionForm
from changelogs.models import Project, Version
from changelogs.serializers import ProjectSerializer, VersionSerializer


class IndexView(View):
    def get(self, request):
        template = loader.get_template("changelogs/index.html")
        context = {}
        return HttpResponse(template.render(context, request))


class FeedView(View):
    def get(self, request):
        template = loader.get_template("changelogs/feed.html")

        if request.user.is_authenticated:
            versions = Version.objects.filter(project__subscribers=request.user).all()
        else:
            versions = Version.objects.filter(project__is_public=True).all()

        context = {"versions": versions}
        return HttpResponse(template.render(context, request))


class ProjectsView(View):
    def get(self, request):
        template = loader.get_template("changelogs/projects.html")
        if request.user.is_authenticated:
            projects_list = (
                Project.objects.accessible_by_user(request.user)
                .filter(subscribers=request.user)
                .order_by("title")
                .all()
            )
        else:
            projects_list = (
                Project.objects.filter(is_public=True).order_by("title").all()
            )

        context = {"projects_list": projects_list}
        return HttpResponse(template.render(context, request))


class ApiDocumentationView(View):
    def get(self, request):
        template = loader.get_template("changelogs/api_documentation.html")
        context = {}
        return HttpResponse(template.render(context, request))


class ProjectDetailView(View):
    def get(self, request, project_id: int):
        template = loader.get_template("changelogs/project_detail.html")
        if request.user.is_anonymous:
            project = get_object_or_404(
                Project.objects.filter(is_public=True), pk=project_id
            )
        else:
            project = get_object_or_404(
                Project.objects.accessible_by_user(request.user), pk=project_id
            )
        context = {"project": project}
        return HttpResponse(template.render(context, request))


class ProjectEditView(View):
    def get(self, request, project_id: int):
        template = loader.get_template("changelogs/edit_project.html")
        project = get_object_or_404(Project, pk=project_id)
        form = ProjectForm(instance=project)
        context = {"project": project, "form": form}
        return HttpResponse(template.render(context, request))

    def post(self, request, project_id: int):
        template = loader.get_template("changelogs/edit_project.html")
        project = get_object_or_404(Project, pk=project_id)
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse("changelogs:project_detail", args=(project.id,))
            )
        else:
            return HttpResponse(template.render({"form": form}, request))


class ProjectVersionsView(View):
    def get(self, request, project_id: int):
        template = loader.get_template("changelogs/project_versions.html")
        project = get_object_or_404(Project, pk=project_id)
        context = {"project": project}
        return HttpResponse(template.render(context, request))


class VersionDetailView(View):
    def get(self, request, project_id: int, version_id: int):
        template = loader.get_template("changelogs/version_detail.html")
        if request.user.is_anonymous:
            project = get_object_or_404(
                Project.objects.filter(is_public=True), pk=project_id
            )
        else:
            project = get_object_or_404(
                Project.objects.accessible_by_user(request.user), pk=project_id
            )
        version = get_object_or_404(
            Version.objects.filter(project=project), pk=version_id
        )
        context = {"version": version}
        return HttpResponse(template.render(context, request))


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        template = loader.get_template("changelogs/profile.html")
        context = {"user": request.user}
        return HttpResponse(template.render(context, request))


class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request):
        template = loader.get_template("changelogs/edit_profile.html")
        form = UserForm(instance=request.user)
        context = {"user": request.user, "form": form}
        return HttpResponse(template.render(context, request))

    def post(self, request):
        template = loader.get_template("changelogs/edit_profile.html")
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("changelogs:profile"))
        else:
            return HttpResponse(template.render({"form": form}, request))


class AboutView(View):
    def get(self, request):
        template = loader.get_template("changelogs/about.html")
        context = {}
        return HttpResponse(template.render(context, request))


class AddProjectView(LoginRequiredMixin, View):
    def get(self, request):
        template = loader.get_template("changelogs/add_project.html")
        form = ProjectForm()
        context = {"form": form}
        return HttpResponse(template.render(context, request))

    def post(self, request):
        template = loader.get_template("changelogs/add_project.html")
        form = ProjectForm(request.POST)
        if form.is_valid():
            project: Project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.subscribers.add(request.user)
            project.save()

            return HttpResponseRedirect(reverse("changelogs:projects"))
        else:
            return HttpResponse(template.render({"form": form}, request))


class AddVersionView(LoginRequiredMixin, View):
    def get(self, request, project_id: int):
        template = loader.get_template("changelogs/add_version.html")
        project = get_object_or_404(
            Project.objects.accessible_by_user(request.user), pk=project_id
        )
        form = VersionForm()
        context = {"project": project, "form": form}
        return HttpResponse(template.render(context, request))

    def post(self, request, project_id: int):
        project = get_object_or_404(Project, pk=project_id)

        template = loader.get_template("changelogs/add_version.html")

        form = VersionForm(request.POST)
        if form.is_valid():
            version = form.instance
            version.date_time = datetime.datetime.now()
            version.project = project
            version.save()

            return HttpResponseRedirect(
                reverse("changelogs:project_versions", args=(project.id,))
            )
        else:
            return HttpResponse(
                template.render({"project": project, "form": form}, request)
            )


class SubscriptionsView(LoginRequiredMixin, View):
    def get(self, request):
        template = loader.get_template("changelogs/subscriptions.html")
        projects_list = (
            Project.objects.accessible_by_user(request.user).order_by("title").all()
        )
        for project in projects_list:
            if project.is_subscribed_by_user(request.user):
                project.is_subscribed = True
            else:
                project.is_subscribed = False
        context = {"projects_list": projects_list}
        return HttpResponse(template.render(context, request))

    def post(self, request):
        projects_list = Project.objects.order_by("title").all()
        for project in projects_list:
            if str(
                project.id
            ) in request.POST.keys() and not project.is_subscribed_by_user(
                request.user
            ):
                project.subscribers.add(request.user)
            if str(
                project.id
            ) not in request.POST.keys() and project.is_subscribed_by_user(
                request.user
            ):
                project.subscribers.remove(request.user)
        return HttpResponseRedirect(reverse("changelogs:subscriptions"))


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
