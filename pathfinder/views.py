# app/views.py

from django.shortcuts import render
from django.views import View
from .forms import RouteForm
from .utils.route_finder import find_route
from .models import Floor, Endpoint
from django.http import JsonResponse
import json
import os
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class EndpointAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        results = []
        if query:
            endpoints = Endpoint.objects.filter(
                Q(name__icontains=query) |
                Q(additional_info__icontains=query)
            )[:20]
        else:
            # Если запрос пустой, возвращаем все или подмножество
            # Например, все первые 20 записей
            # endpoints = Endpoint.objects.all()[:20]
            # на данный момент при пустом запросе возвращаем все
            endpoints = Endpoint.objects.all()

        for ep in endpoints:
            results.append({
                'label': f"{ep.name} - {ep.additional_info}" if ep.additional_info else ep.name,
                'value': f"{ep.name} - {ep.additional_info}" if ep.additional_info else ep.name,
                'node_id': ep.node.id
            })
        return JsonResponse(results, safe=False)

@method_decorator(csrf_exempt, name='dispatch')
class FindRouteView(View):
    def get(self, request):
        form = RouteForm()
        floors = Floor.objects.all().order_by('number')
        # Читаем содержимое SVG-файлов
        floor_svgs = {}
        for floor in floors:
            svg_path = os.path.join(settings.MEDIA_ROOT, floor.svg.name)
            try:
                with open(svg_path, 'r', encoding='utf-8') as svg_file:
                    floor_svgs[floor.number] = svg_file.read()
            except FileNotFoundError:
                floor_svgs[floor.number] = None
        return render(request, 'pathfinder/find_route.html', {'form': form, 'floors': floors, 'floor_svgs': floor_svgs})

    @method_decorator(csrf_exempt, name='dispatch')
    def post(self, request):
        form = RouteForm(request.POST)
        if form.is_valid():
            start_endpoint = form.cleaned_data['start']
            end_endpoint = form.cleaned_data['end']
            route = find_route(start_endpoint.node.id, end_endpoint.node.id)
            if route:
                # Сериализуем данные маршрута
                route_data = [
                    {
                        'id': node.id,
                        'name': node.name,
                        'floor': node.floor.number,
                        'x': node.x,
                        'y': node.y
                    } for node in route
                ]
                return JsonResponse({'status': 'success', 'route': route_data})
            else:
                return JsonResponse({'status': 'error', 'message': 'Маршрут не найден.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Форма содержит ошибки.'})

@method_decorator(csrf_exempt, name='dispatch')
class GetFloorRouteView(View):
    def get(self, request, floor_number):
        route_json = request.GET.get('route')
        if not route_json:
            return JsonResponse({'status': 'error', 'message': 'Маршрут не предоставлен.'}, status=400)

        try:
            route = json.loads(route_json)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Неверный формат маршрута.'}, status=400)

        # Фильтруем узлы маршрута по этажу
        floor_route = [node for node in route if node['floor'] == floor_number]

        # Создаем пары для отрисовки линий маршрута
        lines = []
        for i in range(len(floor_route) - 1):
            from_node = floor_route[i]
            to_node = floor_route[i + 1]
            lines.append({
                'x1': from_node['x'],
                'y1': from_node['y'],
                'x2': to_node['x'],
                'y2': to_node['y'],
            })

        return JsonResponse({'status': 'success', 'lines': lines})

# эндпоин для svg для мобилки
@method_decorator(csrf_exempt, name='dispatch')
class GetFloorSvgView(View):
    def get(self, request, floor_number):
        try:
            floor = Floor.objects.get(number=floor_number)
            svg_path = os.path.join(settings.MEDIA_ROOT, floor.svg.name)
            if os.path.exists(svg_path):
                with open(svg_path, 'r', encoding='utf-8') as svg_file:
                    svg_content = svg_file.read()
                return HttpResponse(svg_content, content_type='image/svg+xml')
            else:
                return HttpResponse(status=404)
        except Floor.DoesNotExist:
            return HttpResponse(status=404)

def get_floors(request):
    floors = Floor.objects.values_list('number', flat=True).order_by('number')
    return JsonResponse(list(floors), safe=False)