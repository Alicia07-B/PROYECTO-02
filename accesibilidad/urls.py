# accesibilidad/urls.py
from django.urls import path
from . import views

# ¡IMPORTANTE! Esta línea define el namespace
app_name = 'accesibilidad'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Encuestas
    path('encuesta/nueva/', views.encuesta_nueva, name='encuesta_nueva'),
    path('encuestas/lista/', views.lista_encuestas, name='lista_encuestas'),
    path('encuestas/crear/', views.crear_encuesta, name='crear_encuesta'),
    path('encuestas/seleccionar/', views.seleccionar_institucion, name='seleccionar_institucion'),
    path('encuestas/<int:encuesta_id>/', views.detalle_encuesta, name='detalle_encuesta'),
    path('encuestas/<int:encuesta_id>/editar/', views.editar_encuesta, name='editar_encuesta'),
    path('encuestas/<int:encuesta_id>/eliminar/', views.eliminar_encuesta, name='eliminar_encuesta'),
    path('encuestas/resultados/', views.resultados_encuestas, name='resultados_encuestas'),
    path('encuestas/<int:encuesta_id>/calificaciones/', views.calificaciones_encuesta, name='calificaciones_encuesta'),
    path('encuesta/<int:encuesta_id>/imprimir/', views.imprimir_encuesta, name='imprimir_encuesta'),
    # Instituciones
    path('instituciones/nueva/', views.nueva_institucion, name='nueva_institucion'),
    path('instituciones/lista/', views.lista_instituciones, name='lista_instituciones'),
    path('instituciones/<int:institucion_id>/', views.detalle_institucion, name='detalle_institucion'),
    path('instituciones/<int:institucion_id>/estadisticas/', views.estadisticas_institucion, name='estadisticas_institucion'),
    
    # Exportar datos
    path('exportar/encuestas/', views.exportar_datos_encuestas, name='exportar_datos_encuestas'),
]