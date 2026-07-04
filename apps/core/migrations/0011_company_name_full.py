"""Standardize company display name to BLUE LAGOON HOLIDAY CRUISES."""

from __future__ import annotations

from django.db import migrations, models

COMPANY_NAME = "BLUE LAGOON HOLIDAY CRUISES"
COPYRIGHT = "© BLUE LAGOON HOLIDAY CRUISES"


def update_company_name(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    for settings in SiteSettings.objects.all():
        settings.company_name = COMPANY_NAME
        settings.copyright_text = COPYRIGHT
        settings.save(update_fields=["company_name", "copyright_text"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_site_social_and_locations"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="company_name",
            field=models.CharField(default="BLUE LAGOON HOLIDAY CRUISES", max_length=200),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="copyright_text",
            field=models.CharField(default="© BLUE LAGOON HOLIDAY CRUISES", max_length=200),
        ),
        migrations.RunPython(update_company_name, migrations.RunPython.noop),
    ]
