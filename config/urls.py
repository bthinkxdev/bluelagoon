"""Root URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import GallerySitemap, PackageSitemap, StaticViewSitemap
from core.views_misc import robots_txt
from packages.views import destination_autocomplete

admin.site.site_header = "BLUE LAGOON HOLIDAY CRUISES CMS"
admin.site.site_title = "BLUE LAGOON HOLIDAY CRUISES"
admin.site.index_title = "Manage banners, packages, gallery & contact messages"

sitemaps = {
    "static": StaticViewSitemap,
    "packages": PackageSitemap,
    "gallery": GallerySitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("", include("website.urls")),
    path("gallery/", include("gallery.urls")),
    path("packages/", include("packages.urls")),
    path("api/destinations/", destination_autocomplete, name="destination_api"),
    path("", include("enquiries.urls")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.handler404"
handler403 = "core.views.handler403"
handler500 = "core.views.handler500"
