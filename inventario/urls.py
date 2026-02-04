from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.dashboard_inventario, name='dashboard'),
    path('equipos/', views.lista_equipos, name='lista_equipos'),
    path('equipos/agregar/', views.agregar_equipo, name='agregar_equipo'),
    path('equipos/<int:id>/', views.detalle_equipo, name='detalle_equipo'),
    path('equipos/editar/<int:id>/', views.editar_equipo, name='editar_equipo'),
    path('mantenimientos/', views.lista_mantenimientos, name='lista_mantenimientos'),
    path('mantenimientos/agregar/', views.agregar_mantenimiento, name='agregar_mantenimiento'),
    path('mantenimientos/agregar/<int:equipo_id>/', views.agregar_mantenimiento, name='agregar_mantenimiento_equipo'),
]