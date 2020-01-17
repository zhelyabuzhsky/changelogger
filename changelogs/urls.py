from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "changelogs"

router = routers.DefaultRouter()
router.register(r"projects", views.ProjectViewSet)
router.register(r"versions", views.VersionViewSet)

urlpatterns = [
    path("", views.index, name="index"),
    path("feed/", views.feed, name="feed"),
    path("profile/", views.profile, name="profile"),
    path("about/", views.about, name="about"),
    path(
        "subscriptions/",
        views.ManageSubscriptionsView.as_view(),
        name="manage_subscriptions",
    ),
    path("projects/", views.projects, name="projects"),
    path("projects/add", views.AddProjectView.as_view(), name="add_project",),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
    path(
        "projects/<int:project_id>/versions/",
        views.project_versions,
        name="project_versions",
    ),
    path(
        "projects/<int:project_id>/versions/<int:version_id>/",
        views.version_detail,
        name="version_detail",
    ),
    path(
        "projects/<int:project_id>/versions/add",
        views.AddVersionView.as_view(),
        name="add_version",
    ),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/documentation/", views.api_documentation, name="api_documentation"),
]
