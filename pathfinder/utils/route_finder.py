# app/utils/route_finder.py

import math
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
            G.add_node(
                node.id,
                floor=node.floor.number,
                x=node.x,
                y=node.y,
                name=node.name
            )

        edges = Edge.objects.all()
        for edge in edges:
            G.add_edge(
                edge.from_node.id,
                edge.to_node.id,
                weight=edge.distance
            )

        # Кешируем граф на 24 часа
        cache.set('building_graph', G, timeout=86400)

    return G


def heuristic(a, b, G):
    """
    Эвристическая функция для A*.
    Использует евклидово расстояние между узлами
    с учетом разницы этажей.
    """
    ax, ay, af = G.nodes[a]['x'], G.nodes[a]['y'], G.nodes[a]['floor']
    bx, by, bf = G.nodes[b]['x'], G.nodes[b]['y'], G.nodes[b]['floor']

    planar_distance = math.hypot(ax - bx, ay - by)
    floor_penalty = abs(af - bf) * 10  # коэффициент можно откорректировать

    return planar_distance + floor_penalty


def find_route(start_node_id, end_node_id):
    """
    Находит кратчайший маршрут между двумя узлами
    с использованием алгоритма A*.

    :param start_node_id: ID начального узла
    :param end_node_id: ID конечного узла
    :return: Список объектов Node, представляющих маршрут, или None
    """
    G = build_graph()

    try:
        path = nx.astar_path(
            G,
            source=start_node_id,
            target=end_node_id,
            heuristic=lambda a, b: heuristic(a, b, G),
            weight='weight'
        )

        route = list(
            Node.objects
            .filter(id__in=path)
            .select_related('floor')
        )

        id_to_node = {node.id: node for node in route}
        sorted_route = [id_to_node[node_id] for node_id in path]

        return sorted_route

    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def invalidate_graph_cache():
    """
    Инвалидирует кеш графа.
    """
    cache.delete('building_graph')
