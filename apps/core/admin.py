"""Django admin — site settings and homepage banners only."""

from django.contrib import admin, messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html

from core.email import get_from_email, get_notification_email
from core.forms import SiteSettingsAdminForm
from core.models import Banner, PageHero, SiteSettings
from core.page_heroes import HERO_DESKTOP_UPLOAD_HELP, HERO_MOBILE_UPLOAD_HELP


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsAdminForm
    fieldsets = (
        ("Company", {"fields": ("company_name", "logo", "copyright_text")}),
        (
            "Contact",
            {
                "fields": (
                    "phone_primary",
                    "email",
                    "address",
                    "head_office",
                    "maps_url",
                )
            },
        ),
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
                    "instagram_url",
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
                subject="BLUE LAGOON HOLIDAY CRUISES — SMTP test",
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


@admin.register(PageHero)
class PageHeroAdmin(admin.ModelAdmin):
    list_display = (
        "page_key",
        "live_path_display",
        "image_preview",
        "mobile_image_preview",
        "is_active",
        "updated_at",
    )
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    readonly_fields = (
        "live_path_display",
        "image_preview_large",
        "mobile_image_preview_large",
        "created_at",
        "updated_at",
    )
    fields = (
        "page_key",
        "live_path_display",
        "image",
        "image_preview_large",
        "mobile_image",
        "mobile_image_preview_large",
        "is_active",
        "created_at",
        "updated_at",
    )
    ordering = ("page_key",)

    @admin.display(description="Live URL")
    def live_path_display(self, obj: PageHero) -> str:
        if not obj:
            return ""
        return obj.live_path or "—"

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj is not None:
            readonly.insert(0, "page_key")
        return readonly

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "page_key":
            used = set(PageHero.objects.values_list("page_key", flat=True))
            kwargs["choices"] = [
                choice for choice in PageHero.PageKey.choices if choice[0] not in used
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "image":
            formfield.help_text = HERO_DESKTOP_UPLOAD_HELP
        if db_field.name == "mobile_image":
            formfield.help_text = HERO_MOBILE_UPLOAD_HELP
        return formfield

    @admin.display(description="Mobile")
    def mobile_image_preview(self, obj: PageHero) -> str:
        if obj.mobile_image:
            return format_html(
                '<img src="{}" alt="" style="max-height:48px;max-width:96px;object-fit:cover;border-radius:4px;">',
                obj.mobile_image.url,
            )
        return "—"

    @admin.display(description="Mobile preview")
    def mobile_image_preview_large(self, obj: PageHero) -> str:
        if obj.mobile_image:
            return format_html(
                '<img src="{}" alt="" style="max-width:100%;max-height:200px;object-fit:contain;border-radius:8px;border:1px solid #ddd;">',
                obj.mobile_image.url,
            )
        return "No mobile image — the desktop hero is used on phones until you upload one."

    @admin.display(description="Preview")
    def image_preview(self, obj: PageHero) -> str:
        if obj.image:
            return format_html(
                '<img src="{}" alt="" style="max-height:48px;max-width:160px;object-fit:cover;border-radius:4px;">',
                obj.image.url,
            )
        return "—"

    @admin.display(description="Preview")
    def image_preview_large(self, obj: PageHero) -> str:
        if obj.image:
            return format_html(
                '<img src="{}" alt="" style="max-width:100%;max-height:200px;object-fit:contain;border-radius:8px;border:1px solid #ddd;">',
                obj.image.url,
            )
        return "No image uploaded yet — the site shows a placeholder until you upload one."

    def has_add_permission(self, request):
        return PageHero.objects.count() < len(PageHero.PageKey)

    def has_delete_permission(self, request, obj=None):
        return False
