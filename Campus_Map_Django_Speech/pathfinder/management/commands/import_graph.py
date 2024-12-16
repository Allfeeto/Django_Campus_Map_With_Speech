# app/management/commands/import_graph.py
import csv
from django.core.management.base import BaseCommand
from pathfinder.models import Floor, Node, Edge

class Command(BaseCommand):
    help = 'Импорт узлов и ребер графа из CSV-файлов'

    # Удаляем существующие данные
    Node.objects.all().delete()
    Edge.objects.all().delete()


    def add_arguments(self, parser):
        parser.add_argument('nodes_csv', type=str, help='Путь к файлу узлов CSV')
        parser.add_argument('edges_csv', type=str, help='Путь к файлу ребер CSV')

    def handle(self, *args, **kwargs):
        nodes_csv = kwargs['nodes_csv']
        edges_csv = kwargs['edges_csv']

        with open(nodes_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                floor_number = int(row['floor'])
                floor, created = Floor.objects.get_or_create(number=floor_number)
                node, created = Node.objects.get_or_create(
                    name=row['name'],
                    floor=floor,
                    x=float(row['x']),
                    y=float(row['y'])
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Создан узел: {node}"))

        with open(edges_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                from_node = Node.objects.get(name=row['from'])
                to_node = Node.objects.get(name=row['to'])
                distance = float(row['distance'])
                edge, created = Edge.objects.get_or_create(
                    from_node=from_node,
                    to_node=to_node,
                    distance=distance
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Создано ребро: {edge}"))


# запуск
# import_graph nodes.csv edges.csv