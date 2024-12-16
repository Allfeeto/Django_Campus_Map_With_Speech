from django.contrib import admin
from .models import Node, Edge, Floor, Endpoint

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'x', 'y', 'floor')  # Отображаемые поля
    list_filter = ('floor',)  # Фильтр по этажу
    search_fields = ('name',)  # Поиск по имени узла
    list_editable = ('x', 'y')  # Позволяем редактировать x и y прямо в списке

@admin.register(Edge)
class EdgeAdmin(admin.ModelAdmin):
    list_display = ('from_node', 'to_node', 'distance')  # Отображаемые поля
    search_fields = ('from_node__name', 'to_node__name')  # Поиск по узлам
    list_editable = ('to_node', 'distance')  # Позволяем редактировать to_node и distance прямо в списке

@admin.register(Floor)
class EdgeFloor(admin.ModelAdmin):
    list_display = ('number', 'svg')  # Отображаемые поля

@admin.register(Endpoint)
class EndpointAdmin(admin.ModelAdmin):
    list_display = ['name', 'node', 'additional_info']
    search_fields = ['name', 'additional_info']