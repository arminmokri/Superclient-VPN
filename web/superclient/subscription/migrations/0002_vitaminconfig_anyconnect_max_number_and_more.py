# Generated by Django 4.1.1 on 2023-02-14 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscription", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="vitaminconfig",
            name="anyconnect_max_number",
            field=models.IntegerField(default=20),
        ),
        migrations.AddField(
            model_name="vitaminconfig",
            name="openvpn_max_number",
            field=models.IntegerField(default=20),
        ),
        migrations.AddField(
            model_name="vitaminconfig",
            name="v2ray_max_number",
            field=models.IntegerField(default=20),
        ),
    ]
