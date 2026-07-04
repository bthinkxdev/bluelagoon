# Generated on server — keep for migration graph compatibility.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("packages", "0007_page_hero_mobile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="package",
            name="hero_banner_mobile",
            field=models.ImageField(
                blank=True,
                help_text=(
                    "Mobile hero — upload exactly 390×400 px (or 780×800 px @2x). "
                    "Falls back to desktop hero if empty."
                ),
                null=True,
                upload_to="packages/hero/mobile/",
            ),
        ),
    ]
