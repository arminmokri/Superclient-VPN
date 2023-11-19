import sys
from django.apps import AppConfig


class ActionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "superclient.action"

    def ready(self):
        unregister_admin()

        if "runserver" in sys.argv:
            from superclient.action.task import start

            start()


def unregister_admin():
    from django.contrib import admin
    from django.contrib.auth.models import Group

    admin.site.unregister(Group)
