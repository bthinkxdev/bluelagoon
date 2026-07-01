"""Django admin — contact form submissions."""

from django.contrib import admin

from enquiries.models import ContactEnquiry


@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "package", "created_at", "is_read", "email_sent", "confirmation_sent")
    list_filter = ("is_read", "email_sent", "confirmation_sent", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone", "message", "package__title")
    readonly_fields = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "message",
        "package",
        "ip_address",
        "email_sent",
        "confirmation_sent",
        "created_at",
        "updated_at",
    )
    list_editable = ("is_read",)
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False
