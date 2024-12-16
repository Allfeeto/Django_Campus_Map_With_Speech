import csv
from pathfinder.models import Node, Edge, Floor

def import_data():
    # Удаляем существующие данные
    Node.objects.all().delete()
    Edge.objects.all().delete()

    # Импорт узлов
    with open('nodes.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            floor_number = int(row['floor'])
            floor, created = Floor.objects.get_or_create(number=floor_number)
            Node.objects.create(
                name=row['id'],
                x=int(row['x']),
                y=int(row['y']),
                floor=floor
            )
    print("Nodes imported successfully.")

    # Импорт рёбер
    with open('edges.csv', 'r') as file:
        reader = csv.DictReader(file)

        # Проверяем, что столбцы "from" и "to" есть в файле
        required_fields = {'from', 'to'}
        if not required_fields.issubset(reader.fieldnames):
            raise ValueError(f"Missing required columns in edges.csv. Found: {reader.fieldnames}")

        for row in reader:
            from_node = Node.objects.get(name=row['from'])
            to_node = Node.objects.get(name=row['to'])

            # Обработка веса
            weight_value = row.get('weight')  # Получаем значение веса
            try:
                weight = float(weight_value) if weight_value not in [None, ''] else 1.0
            except ValueError:
                weight = 1.0  # Если вес некорректный, устанавливаем 1.0

            Edge.objects.create(
                from_node=from_node,
                to_node=to_node,
                distance=weight
            )
    print("Edges imported successfully.")

#from pathfinder.scripts import import_data
#import_data()