import json
from django.core.management.base import BaseCommand
from django.core import serializers
from pathfinder.models import Floor, Node, Edge, Endpoint


class Command(BaseCommand):
    help = 'Export data with UTF-8 encoding'

    def handle(self, *args, **options):
        data = serializers.serialize('json', [
            *Floor.objects.all(),
            *Node.objects.all(),
            *Edge.objects.all(),
            *Endpoint.objects.all()
        ], ensure_ascii=False, indent=2)

        with open('data_utf8.json', 'w', encoding='utf-8') as f:
            f.write(data)