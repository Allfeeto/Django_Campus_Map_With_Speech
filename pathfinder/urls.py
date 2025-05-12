from django.urls import path
from . import views

urlpatterns = [
    path('find-route/', views.FindRouteView.as_view(), name='find_route'),
    path('get-floor-route/<int:floor_number>/', views.GetFloorRouteView.as_view(), name='get_floor_route'),
    path('endpoint-autocomplete/', views.EndpointAutocompleteView.as_view(), name='endpoint_autocomplete'),
    path('floor-svg/<int:floor_number>/', views.GetFloorSvgView.as_view(), name='get_floor_svg'),
    path('floors/', views.get_floors, name='floors'),

    # Другие маршруты
]
