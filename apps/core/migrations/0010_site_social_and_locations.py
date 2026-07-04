"""Update site social links, Mattanur address, and head office."""

from __future__ import annotations

from django.db import migrations, models

MATTANUR_ADDRESS = "Hira Center, Government Hospital Road, Mattanur, Kannur, Kerala 670702"
MAPS_URL = "https://maps.app.goo.gl/hDhERSdhUT3pFz9i6"
FACEBOOK_URL = "https://www.facebook.com/share/1CedRrDnzy/"
INSTAGRAM_URL = "https://www.instagram.com/bluelagoonholidaycruises/"
MAPS_EMBED = (
    '<iframe src="https://maps.google.com/maps?q='
    "Hira+Center,+Government+Hospital+Road,+Mattanur,+Kannur,+Kerala+670702"
    '&output=embed" width="100%" height="360" style="border:0;" '
    'allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
)


def update_site_settings(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    for settings in SiteSettings.objects.all():
        settings.address = MATTANUR_ADDRESS
        settings.head_office = "Cochin"
        settings.maps_url = MAPS_URL
        settings.facebook_url = FACEBOOK_URL
        settings.instagram_url = INSTAGRAM_URL
        settings.google_maps_embed = MAPS_EMBED
        settings.save(
            update_fields=[
                "address",
                "head_office",
                "maps_url",
                "facebook_url",
                "instagram_url",
                "google_maps_embed",
            ]
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_update_primary_phone"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="head_office",
            field=models.CharField(
                blank=True,
                default="Cochin",
                help_text="Head office location shown separately from the branch address.",
                max_length=200,
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="maps_url",
            field=models.URLField(
                blank=True,
                default="https://maps.app.goo.gl/hDhERSdhUT3pFz9i6",
                help_text="Google Maps link for the primary office.",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="instagram_url",
            field=models.URLField(
                blank=True,
                default="https://www.instagram.com/bluelagoonholidaycruises/",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="address",
            field=models.TextField(
                default="Hira Center, Government Hospital Road, Mattanur, Kannur, Kerala 670702"
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="facebook_url",
            field=models.URLField(
                blank=True,
                default="https://www.facebook.com/share/1CedRrDnzy/",
            ),
        ),
        migrations.RunPython(update_site_settings, migrations.RunPython.noop),
    ]
