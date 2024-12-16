# app/utils/route_finder.py

import networkx as nx
from django.core.cache import cache
from pathfinder.models import Node, Edge


def build_graph():
    """
    Создает граф из узлов и ребер, используя библиотеку networkx.
    Кеширует граф для повышения производительности.
    """
    G = cache.get('building_graph')
    if G is None:
        G = nx.Graph()
        nodes = Node.objects.select_related('floor').all()
        for node in nodes:
            G.add_node(node.id, floor=node.floor.number, x=node.x, y=node.y, name=node.name)

        edges = Edge.objects.all()
        for edge in edges:
            G.add_edge(edge.from_node.id, edge.to_node.id, weight=edge.distance)

        # Кешируем граф на 24 часа (86400 секунд)
        cache.set('building_graph', G, timeout=86400)

    return G


def find_route(start_node_id, end_node_id):
    """
    Находит кратчайший маршрут между двумя узлами с использованием алгоритма Дейкстры.

    :param start_node_id: ID начального узла
    :param end_node_id: ID конечного узла
    :return: Список объектов Node, представляющих маршрут, или None, если маршрут не найден
    """
    G = build_graph()
    try:
        path = nx.dijkstra_path(G, source=start_node_id, target=end_node_id, weight='weight')
        # Получаем объекты Node в порядке маршрута
        route = list(Node.objects.filter(id__in=path).select_related('floor'))
        # Сортируем объекты Node в порядке прохождения маршрута
        id_to_node = {node.id: node for node in route}
        sorted_route = [id_to_node[node_id] for node_id in path]
        return sorted_route
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def invalidate_graph_cache():
    """
    Функция для инвалидирования кеша графа, например, после обновления узлов или ребер.
    """
    cache.delete('building_graph')
