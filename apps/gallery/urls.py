"""URL configuration for gallery app."""

from django.urls import path

from gallery import views

app_name = "gallery"

urlpatterns = [
    path("", views.gallery_list, name="list"),
]
