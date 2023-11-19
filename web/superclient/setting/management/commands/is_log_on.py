from django.core.management.base import BaseCommand
from ...models import General


class Command(BaseCommand):
    help = "Get log status"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        if General.objects.first().log:
            print("yes")
        else:
            print("no")
