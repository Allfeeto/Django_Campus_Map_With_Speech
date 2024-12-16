# app/models.py
from django.db import models

class Floor(models.Model):
    number = models.IntegerField(unique=True)
    svg = models.FileField(upload_to='floor_svgs/')  # Схема этажа

    def __str__(self):
        return f"Этаж {self.number}"

class Node(models.Model):
    name = models.CharField(max_length=100)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='nodes')
    x = models.FloatField()  # Координаты на схеме
    y = models.FloatField()

    def __str__(self):
        return f"{self.name} (Этаж {self.floor.number})"

class Edge(models.Model):
    from_node = models.ForeignKey(Node, related_name='edges_from', on_delete=models.CASCADE)
    to_node = models.ForeignKey(Node, related_name='edges_to', on_delete=models.CASCADE)
    distance = models.FloatField()

    def __str__(self):
        return f"{self.from_node} -> {self.to_node} ({self.distance})"

class Endpoint(models.Model):
    node = models.OneToOneField(Node, on_delete=models.CASCADE, related_name='endpoint')
    name = models.CharField(max_length=100, unique=True)  # Например, "Аудитория 5"
    additional_info = models.TextField(blank=True, null=True)  # Фамилии преподавателей

    def __str__(self):
        return self.name