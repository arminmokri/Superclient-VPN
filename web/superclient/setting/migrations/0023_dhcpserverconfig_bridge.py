# Generated by Django 4.1.1 on 2022-12-22 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("setting", "0022_lanconfig_dhcp_set_default_gateway_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="dhcpserverconfig",
            name="bridge",
            field=models.BooleanField(default=True),
        ),
    ]
