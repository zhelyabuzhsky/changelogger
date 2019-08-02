from django.urls import path

from . import views

app_name = 'changelogs'

urlpatterns = [
    path('', views.index, name='index'),
]
