from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    help = "Creates general non-interactively if it doesn't exist"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        if General.objects.count() == 0:
            s = General(id=1)
            s.save()
