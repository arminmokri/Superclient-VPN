# Generated by Django 4.1.1 on 2022-11-06 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vpn", "0014_v2rayurlconfig_remove_configuration_host_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="configuration",
            name="last_log",
            field=models.CharField(blank=True, max_length=4098),
        ),
    ]