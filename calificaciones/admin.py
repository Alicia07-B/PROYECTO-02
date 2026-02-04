from django.contrib import admin
from .models import Estudiante, Docente, Asignatura, Calificacion

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('nombres_completos', 'cedula', 'grado', 'paralelo', 'jornada')
    list_filter = ('grado', 'paralelo', 'jornada', 'sexo')
    search_fields = ('nombres_completos', 'cedula')
    ordering = ('nombres_completos',)

@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ('nombres_completos', 'cedula', 'correo')
    search_fields = ('nombres_completos', 'cedula')

@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'get_nombre_display', 'docente', 'horas_semanales')
    list_filter = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'asignatura', 'trimestre', 'promedio_final_100')
    list_filter = ('trimestre', 'asignatura', 'estudiante__grado')
    search_fields = ('estudiante__nombres_completos', 'asignatura__nombre')
    ordering = ('estudiante', 'asignatura', 'trimestre')