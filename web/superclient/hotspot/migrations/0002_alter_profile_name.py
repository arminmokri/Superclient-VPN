# Generated by Django 4.1.1 on 2022-10-14 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hotspot", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="name",
            field=models.CharField(max_length=256, unique=True),
        ),
    ]