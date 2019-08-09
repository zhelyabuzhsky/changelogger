from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "changelogs"

router = routers.DefaultRouter()
router.register(r"projects", views.ProjectViewSet)

urlpatterns = [
    path("", views.index, name="index"),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
