# Generated by Django 4.1.1 on 2022-12-19 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("setting", "0020_alter_general_check_vpn_curl_timeout_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="general",
            name="default_gateway",
            field=models.CharField(blank=True, max_length=16),
        ),
        migrations.AddField(
            model_name="general",
            name="default_gateway_mode",
            field=models.CharField(
                choices=[("dhcp", "Dhcp"), ("manual", "Manual")],
                default="dhcp",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="general",
            name="timezone",
            field=models.CharField(default="GMT", max_length=128),
        ),
    ]
