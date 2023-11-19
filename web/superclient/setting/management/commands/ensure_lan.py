from django.core.management.base import BaseCommand
from ...models import LanConfig
from ....action.service.Network_Util import *


class Command(BaseCommand):
    help = "Creates lan non-interactively if it doesn't exist"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        if LanConfig.objects.count() == 0:
            s = LanConfig(interface=Network_Util().get_first_lan_interface())
            s.save()
