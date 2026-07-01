"""URL configuration for website app."""

from django.urls import path

from website import views

app_name = "website"

urlpatterns = [
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("pages/<slug:slug>/", views.landing_page, name="landing"),
]
