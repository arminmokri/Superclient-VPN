from django.core.management.base import BaseCommand
from ...service.Network import *


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        n = Network()
        n.Apply()
