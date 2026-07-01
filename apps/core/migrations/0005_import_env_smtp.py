"""One-time import of EMAIL_* values from environment into SiteSettings."""

from __future__ import annotations

import os

from django.db import migrations


def import_env_smtp(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    site, _ = SiteSettings.objects.get_or_create(pk=1)
    if site.smtp_host:
        return
    host = os.environ.get("EMAIL_HOST", "").strip()
    if not host:
        return
    site.smtp_enabled = True
    site.smtp_host = host
    site.smtp_port = int(os.environ.get("EMAIL_PORT", "587") or 587)
    site.smtp_use_tls = os.environ.get("EMAIL_USE_TLS", "True").lower() in ("1", "true", "yes")
    site.smtp_username = os.environ.get("EMAIL_HOST_USER", "").strip()
    site.smtp_password = os.environ.get("EMAIL_HOST_PASSWORD", "").strip()
    site.email_from = os.environ.get("DEFAULT_FROM_EMAIL", "").strip() or site.email
    site.email_notification_to = (
        os.environ.get("CONTACT_NOTIFICATION_EMAIL", "").strip() or site.email
    )
    site.email_notification_bcc = os.environ.get("CONTACT_BCC_EMAIL", "").strip()
    site.save()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_sitesettings_smtp"),
    ]

    operations = [
        migrations.RunPython(import_env_smtp, migrations.RunPython.noop),
    ]
