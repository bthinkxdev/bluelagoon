"""Set primary contact phone to +91 98463 08744."""

from __future__ import annotations

from django.db import migrations, models

NEW_PRIMARY = "+91 98463 08744"
OLD_PRIMARY_DIGITS = "9446651610"
NEW_PRIMARY_DIGITS = "9846308744"


def _digits(value: str) -> str:
    return "".join(char for char in (value or "") if char.isdigit())


def forwards(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    OfficeBranch = apps.get_model("core", "OfficeBranch")

    for settings in SiteSettings.objects.all():
        changed = False
        if _digits(settings.phone_primary).endswith(OLD_PRIMARY_DIGITS):
            settings.phone_primary = NEW_PRIMARY
            changed = True
        if _digits(settings.phone_secondary).endswith(NEW_PRIMARY_DIGITS):
            settings.phone_secondary = ""
            changed = True
        if changed:
            settings.save(update_fields=["phone_primary", "phone_secondary"])

    for branch in OfficeBranch.objects.all():
        changed = False
        if _digits(branch.phone_primary).endswith(OLD_PRIMARY_DIGITS):
            branch.phone_primary = NEW_PRIMARY
            changed = True
        if _digits(branch.phone_secondary).endswith(NEW_PRIMARY_DIGITS):
            branch.phone_secondary = ""
            changed = True
        if changed:
            branch.save(update_fields=["phone_primary", "phone_secondary"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_page_hero_mobile"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="sitesettings",
            name="phone_primary",
            field=models.CharField(default="+91 98463 08744", max_length=30),
        ),
    ]
