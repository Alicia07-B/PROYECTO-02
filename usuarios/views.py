# usuarios/views.py - VERSIÓN COMPLETA
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# ========== AUTHENTICATION ==========
def login_view(request):
    """Vista personalizada para login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'✅ Bienvenido/a, {user.username}!')
            return redirect('usuarios_dashboard')
        else:
            messages.error(request, '❌ Usuario o contraseña incorrectos')
    
    # Si ya está autenticado, redirige al dashboard
    if request.user.is_authenticated:
        return redirect('usuarios_dashboard')
    
    return render(request, 'usuarios/login.html')

def logout_view(request):
    """Vista personalizada para logout"""
    logout(request)
    messages.success(request, '✅ Has cerrado sesión exitosamente.')
    return redirect('login')

# ========== DASHBOARD ==========
@login_required
def dashboard(request):
    # Importar dinámicamente para evitar circular imports
    try:
        from calificaciones.models import Estudiante, Calificacion, Docente
        estudiantes_count = Estudiante.objects.count()
        calificaciones_count = Calificacion.objects.count()
        docentes_count = Docente.objects.count()
    except:
        estudiantes_count = 0
        calificaciones_count = 0
        docentes_count = 0
    
    context = {
        'estudiantes_count': estudiantes_count,
        'calificaciones_count': calificaciones_count,
        'docentes_count': docentes_count,
        'user': request.user,
    }
    return render(request, 'usuarios/dashboard.html', context)