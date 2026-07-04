# Generated on server — keep for migration graph compatibility.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_update_primary_phone"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pagehero",
            name="mobile_image",
            field=models.ImageField(
                blank=True,
                help_text=(
                    "Mobile — upload exactly 390×400 px (or 780×800 px @2x). "
                    "Falls back to the desktop image if empty."
                ),
                upload_to="page-heroes/mobile/",
            ),
        ),
    ]
