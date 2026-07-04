# Merge core migration branches created on server and in app updates.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_alter_pagehero_mobile_image"),
        ("core", "0011_company_name_full"),
    ]

    operations = []
