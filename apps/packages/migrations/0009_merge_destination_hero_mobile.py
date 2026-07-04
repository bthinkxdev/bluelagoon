# Merge packages migration branches created on server and in app updates.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("packages", "0008_alter_package_hero_banner_mobile"),
        ("packages", "0008_destination"),
    ]

    operations = []
