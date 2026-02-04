# calificaciones/urls.py
from django.urls import path
from . import views

app_name = 'calificaciones'

urlpatterns = [
    # ========== SISTEMA PRINCIPAL ==========
    path('sistema/', views.sistema_calificaciones, name='sistema_calificaciones'),
    path('', views.sistema_calificaciones, name='home'),
    
    # ========== PDFs ==========
    path('sistema/pdf/', views.generar_pdf_sistema_calificaciones, name='pdf_sistema_calificaciones'),
    path('sistema/guardar/', views.guardar_calificaciones_ajax, name='guardar_calificaciones_ajax'),
    
    # ========== LISTAS ==========
    path('lista/', views.lista_calificaciones, name='lista_calificaciones'),
    path('estudiantes/', views.lista_estudiantes, name='lista_estudiantes'),
    path('docentes/', views.lista_docentes, name='lista_docentes'),
    path('asignaturas/', views.lista_asignaturas, name='lista_asignaturas'),
    
    # ========== AGREGAR ==========
    path('estudiantes/agregar/', views.agregar_estudiante, name='agregar_estudiante'),
    path('docentes/agregar/', views.agregar_docente, name='agregar_docente'),
    path('asignaturas/agregar/', views.agregar_asignatura, name='agregar_asignatura'),
    path('agregar/', views.agregar_calificacion, name='agregar_calificacion'),
    
    # ========== EDITAR ==========
    # Cambiar 'id' por 'id_estudiante', 'id_docente', 'id_asignatura'
    path('estudiantes/editar/<int:id_estudiante>/', views.editar_estudiante, name='editar_estudiante'),
    path('docentes/editar/<int:id_docente>/', views.editar_docente, name='editar_docente'),
    path('asignaturas/editar/<int:id_asignatura>/', views.editar_asignatura, name='editar_asignatura'),
    path('editar/<int:id_calificacion>/', views.editar_calificacion, name='editar_calificacion'),
    
    # ========== ELIMINAR ==========
    path('estudiantes/eliminar/<int:id_estudiante>/', views.eliminar_estudiante, name='eliminar_estudiante'),
    path('docentes/eliminar/<int:id_docente>/', views.eliminar_docente, name='eliminar_docente'),
    path('asignaturas/eliminar/<int:id_asignatura>/', views.eliminar_asignatura, name='eliminar_asignatura'),
    path('eliminar/<int:id_calificacion>/', views.eliminar_calificacion, name='eliminar_calificacion'),
    
    # ========== REPORTES ==========
    path('reportes/', views.boleta_calificaciones, name='boleta_trimestre'),
    path('reportes/pdf/<int:estudiante_id>/', views.generar_reporte_pdf, name='generar_reporte_pdf'),
    
    # ========== DASHBOARD Y BÚSQUEDA ==========
    path('dashboard/', views.dashboard_estadisticas, name='dashboard_estadisticas'),
    path('busqueda/', views.busqueda_avanzada, name='busqueda_avanzada'),
    
    # ========== AJAX ==========
    path('guardar-masivo/', views.guardar_calificaciones_masivo, name='guardar_calificaciones_masivo'),
 path('boleta/<int:estudiante_id>/trimestre/<int:trimestre>/', 
         views.boleta_estudiante_trimestre, name='boleta_estudiante_trimestre'),
    path('boleta/pdf/<int:estudiante_id>/trimestre/<int:trimestre>/', 
         views.generar_pdf_boleta_trimestre, name='generar_pdf_boleta_trimestre'),

]

