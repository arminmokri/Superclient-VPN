# Generated by Django 4.1.1 on 2022-10-14 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256)),
                ("description", models.CharField(max_length=1028)),
                ("ssid", models.CharField(max_length=128)),
                ("interface", models.CharField(max_length=128)),
                ("wpa_passphrase", models.CharField(max_length=128)),
                ("ip", models.CharField(max_length=16)),
                ("dhcp_ip_from", models.CharField(max_length=16)),
                ("dhcp_ip_to", models.CharField(max_length=16)),
                ("netmask", models.CharField(max_length=20)),
            ],
        ),
    ]