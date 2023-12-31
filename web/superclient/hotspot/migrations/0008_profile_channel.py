# Generated by Django 4.1.1 on 2022-11-02 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hotspot", "0007_delete_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="channel",
            field=models.CharField(
                choices=[
                    ("1", "1"),
                    ("2", "2"),
                    ("3", "3"),
                    ("4", "4"),
                    ("5", "5"),
                    ("6", "6"),
                    ("7", "7"),
                    ("8", "8"),
                    ("9", "9"),
                    ("10", "7"),
                    ("11", "7"),
                    ("12", "12"),
                    ("13", "13"),
                    ("14", "14"),
                ],
                default="6",
                max_length=8,
            ),
        ),
    ]
