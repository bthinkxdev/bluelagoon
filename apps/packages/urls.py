"""URL configuration for packages app."""

from django.urls import path

from packages import views

app_name = "packages"

urlpatterns = [
    path("", views.package_list, name="list"),
    path("list/partial/", views.package_list_partial, name="list_partial"),
    path("api/destinations/", views.destination_autocomplete, name="destination_api"),
    path("domestic/", views.domestic_list, name="domestic_list"),
    path("international/", views.international_list, name="international_list"),
    path("pilgrim/", views.pilgrim_list, name="pilgrim_list"),
    path("domestic/<slug:slug>/", views.domestic_detail, name="domestic_detail"),
    path("international/<slug:slug>/", views.international_detail, name="international_detail"),
    path("pilgrim/<slug:slug>/", views.pilgrim_detail, name="pilgrim_detail"),
]
