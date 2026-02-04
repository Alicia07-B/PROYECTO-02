from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from .models import Equipo, Ubicacion, Mantenimiento
from .forms import EquipoForm, UbicacionForm, MantenimientoForm

@login_required
def dashboard_inventario(request):
    # Estadísticas
    total_equipos = Equipo.objects.count()
    equipos_operativos = Equipo.objects.filter(estado='OPERATIVO').count()
    equipos_mantenimiento = Equipo.objects.filter(estado='MANTENIMIENTO').count()
    total_mantenimientos = Mantenimiento.objects.count()
    
    # Costo total del inventario
    costo_total = Equipo.objects.aggregate(total=Sum('costo'))['total'] or 0
    
    # Últimos mantenimientos
    ultimos_mantenimientos = Mantenimiento.objects.select_related('equipo').order_by('-fecha')[:5]
    
    # Equipos por tipo
    equipos_por_tipo = Equipo.objects.values('tipo').annotate(total=Count('id_equipo'))
    
    context = {
        'total_equipos': total_equipos,
        'equipos_operativos': equipos_operativos,
        'equipos_mantenimiento': equipos_mantenimiento,
        'total_mantenimientos': total_mantenimientos,
        'costo_total': costo_total,
        'ultimos_mantenimientos': ultimos_mantenimientos,
        'equipos_por_tipo': equipos_por_tipo,
    }
    
    return render(request, 'inventario/dashboard.html', context)

@login_required
def lista_equipos(request):
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    estado = request.GET.get('estado', '')
    
    equipos = Equipo.objects.all()
    
    if query:
        equipos = equipos.filter(
            Q(codigo_inventario__icontains=query) |
            Q(marca__icontains=query) |
            Q(modelo__icontains=query) |
            Q(numero_serie__icontains=query)
        )
    
    if tipo:
        equipos = equipos.filter(tipo=tipo)
    
    if estado:
        equipos = equipos.filter(estado=estado)
    
    context = {
        'equipos': equipos,
        'query': query,
        'tipo': tipo,
        'estado': estado,
        'TIPO_CHOICES': Equipo.TIPO_CHOICES,
        'ESTADO_CHOICES': Equipo.ESTADO_CHOICES,
    }
    
    return render(request, 'inventario/equipos/lista.html', context)

@login_required
def detalle_equipo(request, id):
    equipo = get_object_or_404(Equipo, id_equipo=id)
    mantenimientos = Mantenimiento.objects.filter(equipo=equipo).order_by('-fecha')
    
    context = {
        'equipo': equipo,
        'mantenimientos': mantenimientos,
    }
    
    return render(request, 'inventario/equipos/detalle.html', context)

@login_required
def agregar_equipo(request):
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            equipo = form.save()
            messages.success(request, f'✅ Equipo {equipo.codigo_inventario} registrado exitosamente.')
            return redirect('inventario:detalle_equipo', id=equipo.id_equipo)
    else:
        form = EquipoForm()
    
    context = {
        'form': form,
        'titulo': 'Nuevo Equipo',
    }
    
    return render(request, 'inventario/equipos/form.html', context)

@login_required
def editar_equipo(request, id):
    equipo = get_object_or_404(Equipo, id_equipo=id)
    
    if request.method == 'POST':
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Equipo {equipo.codigo_inventario} actualizado exitosamente.')
            return redirect('inventario:detalle_equipo', id=equipo.id_equipo)
    else:
        form = EquipoForm(instance=equipo)
    
    context = {
        'form': form,
        'equipo': equipo,
        'titulo': 'Editar Equipo',
    }
    
    return render(request, 'inventario/equipos/form.html', context)

@login_required
def lista_mantenimientos(request):
    mantenimientos = Mantenimiento.objects.select_related('equipo', 'usuario').order_by('-fecha')
    
    context = {
        'mantenimientos': mantenimientos,
    }
    
    return render(request, 'inventario/mantenimientos/lista.html', context)

@login_required
def agregar_mantenimiento(request, equipo_id=None):
    equipo = None
    if equipo_id:
        equipo = get_object_or_404(Equipo, id_equipo=equipo_id)
    
    if request.method == 'POST':
        form = MantenimientoForm(request.POST)
        if form.is_valid():
            mantenimiento = form.save(commit=False)
            mantenimiento.usuario = request.user
            mantenimiento.save()
            messages.success(request, '✅ Mantenimiento registrado exitosamente.')
            return redirect('inventario:lista_mantenimientos')
    else:
        initial = {'equipo': equipo} if equipo else {}
        form = MantenimientoForm(initial=initial)
    
    context = {
        'form': form,
        'equipo': equipo,
        'titulo': 'Nuevo Mantenimiento',
    }
    
    return render(request, 'inventario/mantenimientos/form.html', context)