from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "changelogs"

router = routers.DefaultRouter()
router.register(r"projects", views.ProjectViewSet)
router.register(r"versions", views.VersionViewSet)

urlpatterns = [
    path("", views.index, name="index"),
    path("projects/all/", views.all_projects, name="all_projects"),
    path("projects/my/", views.my_projects, name="my_projects"),
    path("feed/", views.feed, name="feed"),
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
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
