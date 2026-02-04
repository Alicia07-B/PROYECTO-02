# gesinfra_sistema/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from usuarios.views import dashboard as usuarios_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('usuarios_dashboard')),  # Redirige al dashboard de usuarios
    path('usuarios/', include('usuarios.urls')),
    path('inventario/', include('inventario.urls')),
    path('calificaciones/', include('calificaciones.urls')),
    path('accesibilidad/', include('accesibilidad.urls', namespace='accesibilidad')),  # Con namespace
]