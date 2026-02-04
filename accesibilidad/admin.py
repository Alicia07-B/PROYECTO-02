from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import InstitucionEducativa, EncuestaBarreras

@admin.register(InstitucionEducativa)
class InstitucionEducativaAdmin(admin.ModelAdmin):
    list_display = ('nombre_institucion', 'codigo_amie', 'provincia', 'canton', 'tipo_institucion', 'fecha_registro')
    list_filter = ('tipo_institucion', 'provincia')
    search_fields = ('nombre_institucion', 'codigo_amie')
    ordering = ('nombre_institucion',)

@admin.register(EncuestaBarreras)
class EncuestaBarrerasAdmin(admin.ModelAdmin):
    list_display = ('institucion', 'fecha_encuesta', 'encuestador', 'fecha_registro')
    list_filter = ('fecha_encuesta',)
    search_fields = ('institucion__nombre_institucion', 'encuestador')
    date_hierarchy = 'fecha_encuesta'