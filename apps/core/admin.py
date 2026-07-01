"""Django admin — site settings and homepage banners only."""

from django.contrib import admin, messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html

from core.email import get_from_email, get_notification_email
from core.forms import SiteSettingsAdminForm
from core.models import Banner, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsAdminForm
    fieldsets = (
        ("Company", {"fields": ("company_name", "logo", "copyright_text")}),
        ("Contact", {"fields": ("phone_primary", "email", "address")}),
        (
            "Email delivery (SMTP)",
            {
                "description": (
                    "Configure outgoing mail here. When SMTP is disabled, messages are "
                    "printed to the server console (development)."
                ),
                "fields": (
                    "smtp_enabled",
                    "smtp_host",
                    "smtp_port",
                    "smtp_use_tls",
                    "smtp_use_ssl",
                    "smtp_username",
                    "smtp_password",
                    "email_from",
                    "email_notification_to",
                    "email_notification_bcc",
                    "smtp_test_link",
                ),
            },
        ),
        (
            "Social & map",
            {
                "fields": (
                    "facebook_url",
                    "twitter_url",
                    "youtube_url",
                    "google_maps_embed",
                ),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = ("smtp_test_link",)

    def smtp_test_link(self, obj: SiteSettings) -> str:
        if not obj or not obj.pk:
            return "Save settings first, then send a test email."
        url = reverse("admin:core_sitesettings_test_smtp")
        return format_html('<a class="button" href="{}">Send test email</a>', url)

    smtp_test_link.short_description = "Test SMTP"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "test-smtp/",
                self.admin_site.admin_view(self.test_smtp_view),
                name="core_sitesettings_test_smtp",
            ),
        ]
        return custom + urls

    def test_smtp_view(self, request):
        site = SiteSettings.load()
        to_email = get_notification_email()
        from_email = get_from_email()
        try:
            sent = send_mail(
                subject="Blue Lagoon — SMTP test",
                message="If you received this, SMTP is configured correctly.",
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False,
            )
            if sent:
                messages.success(
                    request,
                    f"Test email sent to {to_email} (from {from_email}).",
                )
            else:
                messages.warning(request, "No message was sent.")
        except Exception as exc:
            messages.error(request, f"SMTP test failed: {exc}")
        return redirect(reverse("admin:core_sitesettings_change", args=(site.pk,)))

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "heading", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "heading", "subtitle")
    ordering = ("order", "id")
    fieldsets = (
        ("Text", {"fields": ("title", "subtitle", "heading", "description")}),
        (
            "Buttons",
            {
                "fields": (
                    "primary_button_text",
                    "primary_button_url",
                    "secondary_button_text",
                    "secondary_button_url",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Images", {"fields": ("desktop_image", "mobile_image")}),
        ("Display", {"fields": ("order", "is_active", "start_date", "end_date")}),
    )
