from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "changelogs"

router = routers.DefaultRouter()
router.register(r"projects", views.ProjectViewSet)
router.register(r"versions", views.VersionViewSet)

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("feed/", views.FeedView.as_view(), name="feed"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit", views.ProfileEditView.as_view(), name="edit_profile"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("subscriptions/", views.SubscriptionsView.as_view(), name="subscriptions",),
    path("projects/", views.ProjectsView.as_view(), name="projects"),
    path("projects/add", views.AddProjectView.as_view(), name="add_project",),
    path(
        "projects/<int:project_id>/",
        views.ProjectDetailView.as_view(),
        name="project_detail",
    ),
    path(
        "projects/<int:project_id>/edit",
        views.ProjectEditView.as_view(),
        name="edit_project",
    ),
    path(
        "projects/<int:project_id>/versions/",
        views.ProjectVersionsView.as_view(),
        name="project_versions",
    ),
    path(
        "projects/<int:project_id>/versions/<int:version_id>/",
        views.VersionDetailView.as_view(),
        name="version_detail",
    ),
    path(
        "projects/<int:project_id>/versions/add",
        views.AddVersionView.as_view(),
        name="add_version",
    ),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path(
        "api/documentation/",
        views.ApiDocumentationView.as_view(),
        name="api_documentation",
    ),
]
