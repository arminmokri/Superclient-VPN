# Generated by Django 4.1.1 on 2022-12-16 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("setting", "0019_alter_general_check_vpn_curl_retry_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="general",
            name="check_vpn_curl_timeout",
            field=models.IntegerField(default=12),
        ),
        migrations.AlterField(
            model_name="general",
            name="check_vpn_ping_timeout",
            field=models.IntegerField(default=4),
        ),
    ]
