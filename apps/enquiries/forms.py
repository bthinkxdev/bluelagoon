"""Contact and enquiry forms."""

from __future__ import annotations

import random

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from enquiries.models import ContactEnquiry, NewsletterSubscription, PackageEnquiry
from packages.models import Package

try:
    from django_recaptcha.fields import ReCaptchaField
    from django_recaptcha.widgets import ReCaptchaV3

    HAS_RECAPTCHA = bool(settings.RECAPTCHA_PUBLIC_KEY and settings.RECAPTCHA_PRIVATE_KEY)
except ImportError:
    HAS_RECAPTCHA = False


class MathCaptchaMixin(forms.Form):
    """Fallback human verification when reCAPTCHA keys are not configured."""

    captcha_answer = forms.IntegerField(
        label="Human verification",
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Your answer"}),
    )
    captcha_expected = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if HAS_RECAPTCHA:
            return
        if not self.is_bound:
            n1, n2 = random.randint(1, 6), random.randint(5, 9)
            self.fields["captcha_expected"].initial = n1 + n2
            self.fields["captcha_answer"].label = f"Human verification: What is {n1} + {n2} = ?"

    def clean(self):
        cleaned = super().clean()
        if HAS_RECAPTCHA:
            return cleaned
        expected = cleaned.get("captcha_expected")
        answer = cleaned.get("captcha_answer")
        if expected is not None and answer != expected:
            raise ValidationError("Wrong verification code.")
        return cleaned


class ContactForm(MathCaptchaMixin, forms.ModelForm):
    """Contact page form with validation."""

    package_slug = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ContactEnquiry
        fields = ("first_name", "last_name", "email", "phone", "message")
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your first name", "autocomplete": "given-name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your last name", "autocomplete": "family-name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "you@example.com", "autocomplete": "email"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+91 98765 43210", "autocomplete": "tel"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Tell us about your trip — destination, dates, group size, and any special requests.",
                    "rows": 5,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].label = "First Name"
        self.fields["last_name"].label = "Last Name"
        self.fields["message"].label = "Message"
        for field_name in ("first_name", "last_name", "email", "phone", "message"):
            self.fields[field_name].required = True
        if HAS_RECAPTCHA:
            self.fields.pop("captcha_answer", None)
            self.fields.pop("captcha_expected", None)
            self.fields["captcha"] = ReCaptchaField(widget=ReCaptchaV3)

    def clean_first_name(self):
        value = self.cleaned_data["first_name"].strip()
        if len(value) < 2 or len(value) > 100:
            raise ValidationError("First name must be between 2 and 100 characters.")
        return value

    def clean_last_name(self):
        value = self.cleaned_data["last_name"].strip()
        if len(value) < 1 or len(value) > 100:
            raise ValidationError("Last name is required.")
        return value

    def clean_message(self):
        value = self.cleaned_data["message"].strip()
        if len(value) < 10 or len(value) > 5000:
            raise ValidationError("Message must be between 10 and 5000 characters.")
        return value

    def clean_phone(self):
        import re

        value = self.cleaned_data["phone"].strip()
        if not re.match(r"^[\d\s\+\-\(\)]{7,20}$", value):
            raise ValidationError("Please enter a valid phone number.")
        return value

    def clean_package_slug(self):
        slug = (self.cleaned_data.get("package_slug") or "").strip()
        if not slug:
            return ""
        package = Package.objects.filter(slug=slug, status=Package.Status.PUBLISHED).first()
        if not package:
            raise ValidationError("The selected package is no longer available.")
        return slug

    def save(self, commit=True):
        instance = super().save(commit=False)
        slug = self.cleaned_data.get("package_slug") or ""
        if slug:
            instance.package = Package.objects.filter(
                slug=slug, status=Package.Status.PUBLISHED
            ).first()
        if commit:
            instance.save()
        return instance


class PackageEnquiryForm(MathCaptchaMixin, forms.ModelForm):
    class Meta:
        model = PackageEnquiry
        fields = ("name", "email", "phone", "travel_date", "guests", "message")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "travel_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "guests": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["travel_date"].required = False
        self.fields["message"].required = False


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Your mail"}
            ),
        }
