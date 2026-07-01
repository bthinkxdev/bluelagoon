"""URL configuration for enquiries app."""

from django.urls import path

from enquiries import views

app_name = "enquiries"

urlpatterns = [
    path("contact/", views.contact, name="contact"),
]
