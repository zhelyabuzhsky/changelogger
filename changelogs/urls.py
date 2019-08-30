from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "changelogs"

router = routers.DefaultRouter()
router.register(r"projects", views.ProjectViewSet)

urlpatterns = [
    path("", views.index, name="index"),
    path("projects/all/", views.all_projects, name="all_projects"),
    path("projects/my/", views.my_projects, name="my_projects"),
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
