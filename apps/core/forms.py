"""Admin forms for core models."""

from __future__ import annotations

from django import forms

from core.models import SiteSettings


class SiteSettingsAdminForm(forms.ModelForm):
    """Keep existing SMTP password when the admin field is left blank."""

    class Meta:
        model = SiteSettings
        fields = "__all__"
        widgets = {
            "smtp_password": forms.PasswordInput(render_value=False),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["smtp_password"].help_text = (
            "Leave blank to keep the current password. Enter a new value to change it."
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.instance.pk and not self.cleaned_data.get("smtp_password"):
            instance.smtp_password = SiteSettings.objects.get(pk=self.instance.pk).smtp_password
        if commit:
            instance.save()
        return instance
