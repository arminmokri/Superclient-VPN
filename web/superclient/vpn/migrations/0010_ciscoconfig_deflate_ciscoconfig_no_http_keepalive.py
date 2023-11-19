# Generated by Django 4.1.1 on 2022-11-03 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vpn", "0009_remove_openvpnconfig_no_deflate_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ciscoconfig",
            name="deflate",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="ciscoconfig",
            name="no_http_keepalive",
            field=models.BooleanField(default=False),
        ),
    ]
