# Generated by Django 4.1.1 on 2022-10-31 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vpn", "0005_alter_configuration_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="configuration",
            name="usable",
        ),
        migrations.AlterField(
            model_name="configuration",
            name="failed",
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AlterField(
            model_name="configuration",
            name="success",
            field=models.IntegerField(default=0, editable=False),
        ),
    ]