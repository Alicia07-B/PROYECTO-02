## calificaciones/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch, cm
from io import BytesIO
import datetime
import json
import csv
import traceback
from .models import Estudiante, Docente, Asignatura, Calificacion
from .forms import EstudianteForm, DocenteForm, AsignaturaForm, CalificacionForm

@login_required
def sistema_calificaciones(request):
    """Sistema principal de calificaciones - LA TABLA"""
    # Obtener parámetros de filtro
    grado = request.GET.get('grado', '')
    asignatura_id = request.GET.get('asignatura', '')
    trimestre = request.GET.get('trimestre', '1')
    paralelo = request.GET.get('paralelo', '')
    
    # Obtener TODOS los estudiantes primero
    todos_estudiantes = Estudiante.objects.all().order_by('nombres_completos')
    
    # Determinar grado por defecto si no se especifica
    if not grado:
        if todos_estudiantes.exists():
            # Tomar el grado del primer estudiante
            grado = todos_estudiantes.first().grado
        else:
            grado = '7EGB'
    
    # Filtrar estudiantes por grado y paralelo
    estudiantes_filtrados = todos_estudiantes.filter(grado=grado)
    if paralelo:
        estudiantes_filtrados = estudiantes_filtrados.filter(paralelo=paralelo)
    
    estudiantes = list(estudiantes_filtrados)
    
    # Obtener asignatura
    asignatura = None
    if asignatura_id:
        try:
            asignatura = Asignatura.objects.get(pk=asignatura_id)
        except Asignatura.DoesNotExist:
            asignatura = None
    else:
        # Si no hay asignatura seleccionada, tomar la primera disponible
        asignaturas_disponibles = Asignatura.objects.all()
        if asignaturas_disponibles.exists():
            asignatura = asignaturas_disponibles.first()
            asignatura_id = str(asignatura.id_asignatura)
    
    # Obtener calificaciones existentes para estos estudiantes
    calificaciones_dict = {}
    if asignatura and estudiantes:
        estudiante_ids = [e.id_estudiante for e in estudiantes]
        calificaciones = Calificacion.objects.filter(
            estudiante_id__in=estudiante_ids,
            asignatura=asignatura,
            trimestre=trimestre
        ).select_related('estudiante')
        
        for cal in calificaciones:
            calificaciones_dict[cal.estudiante.id_estudiante] = cal
    
    # Crear lista combinada de estudiantes con sus calificaciones
    estudiantes_con_calificaciones_list = []
    for estudiante in estudiantes:
        calificacion = calificaciones_dict.get(estudiante.id_estudiante)
        estudiantes_con_calificaciones_list.append({
            'estudiante': estudiante,
            'calificacion': calificacion
        })
    
    # Obtener datos para los filtros
    asignaturas = Asignatura.objects.all()
    
    # Obtener grados disponibles (solo los que existen en la BD)
    GRADOS_QUINTO_A_DECIMO = ['5EGB', '6EGB', '7EGB', '8EGB', '9EGB', '10EGB']
    grados_existentes = list(Estudiante.objects.values_list('grado', flat=True).distinct().order_by('grado'))
    grados_disponibles = [g for g in GRADOS_QUINTO_A_DECIMO if g in grados_existentes]
    
    if not grados_disponibles and grado in GRADOS_QUINTO_A_DECIMO:
        grados_disponibles = [grado]
    
    paralelos_disponibles = list(Estudiante.objects.values_list('paralelo', flat=True).distinct().order_by('paralelo'))
    
    # Calcular estadísticas
    total_estudiantes = len(estudiantes)
    estudiantes_con_datos = sum(1 for item in estudiantes_con_calificaciones_list 
                               if item['calificacion'] and (
                                   item['calificacion'].leccion1 > 0 or 
                                   item['calificacion'].leccion2 > 0 or 
                                   item['calificacion'].actividad_experiencial > 0 or 
                                   item['calificacion'].proyecto_interdisciplinar > 0 or 
                                   item['calificacion'].examen > 0
                               ))
    
    # Información del docente
    docente_info = request.user.get_full_name() or request.user.username
    
    # Obtener año lectivo
    anio_lectivo = "2024-2025"
    if estudiantes:
        anio_lectivo = estudiantes[0].anio_lectivo if estudiantes[0].anio_lectivo else "2024-2025"
    
    # Obtener nombre del trimestre
    TRIMESTRE_CHOICES = {
        1: 'Primer Trimestre',
        2: 'Segundo Trimestre',
        3: 'Tercer Trimestre'
    }
    trimestre_nombre = TRIMESTRE_CHOICES.get(int(trimestre), 'Primer Trimestre')
    
    context = {
        'estudiantes_con_calificaciones_list': estudiantes_con_calificaciones_list,
        'estudiantes': estudiantes,
        'asignaturas': asignaturas,
        'grados': grados_disponibles,
        'paralelos': paralelos_disponibles,
        'asignatura_seleccionada': asignatura,
        'grado_seleccionado': grado,
        'paralelo_seleccionado': paralelo,
        'trimestre_seleccionado': trimestre,
        'total_estudiantes': total_estudiantes,
        'estudiantes_con_datos': estudiantes_con_datos,
        'docente_info': docente_info,
        'anio_lectivo': anio_lectivo,
        'trimestre_nombre': trimestre_nombre,
    }
    
    return render(request, 'calificaciones/sistema.html', context)

@login_required
def guardar_calificaciones_ajax(request):
    """Guardar calificaciones via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            estudiante_id = data.get('estudiante_id')
            asignatura_id = data.get('asignatura_id')
            trimestre = data.get('trimestre')
            campo = data.get('campo')
            valor = data.get('valor')
            
            # Validar datos
            if not all([estudiante_id, asignatura_id, trimestre, campo, valor is not None]):
                return JsonResponse({'success': False, 'error': 'Datos incompletos'})
            
            # Buscar o crear calificación
            calificacion, created = Calificacion.objects.get_or_create(
                estudiante_id=estudiante_id,
                asignatura_id=asignatura_id,
                trimestre=trimestre,
                defaults={
                    'leccion1': 0,
                    'leccion2': 0,
                    'actividad_experiencial': 0,
                    'proyecto_interdisciplinar': 0,
                    'examen': 0
                }
            )
            
            # Actualizar campo
            if campo == 'leccion1':
                calificacion.leccion1 = float(valor) if valor else 0
            elif campo == 'leccion2':
                calificacion.leccion2 = float(valor) if valor else 0
            elif campo == 'actividad_experiencial':
                calificacion.actividad_experiencial = float(valor) if valor else 0
            elif campo == 'proyecto_interdisciplinar':
                calificacion.proyecto_interdisciplinar = float(valor) if valor else 0
            elif campo == 'examen':
                calificacion.examen = float(valor) if valor else 0
            
            # Guardar y recalcular
            calificacion.save()
            
            return JsonResponse({
                'success': True,
                'promedio_formativo': float(calificacion.aporte_formativo_70),
                'promedio_sumativo': float(calificacion.aporte_sumativo_30),
                'promedio_final': float(calificacion.promedio_final_100),
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def generar_pdf_sistema_calificaciones(request):
    """Generar PDF de la tabla del sistema de calificaciones"""
    # Obtener parámetros
    grado = request.GET.get('grado', '')
    asignatura_id = request.GET.get('asignatura', '')
    trimestre = request.GET.get('trimestre', '1')
    paralelo = request.GET.get('paralelo', '')
    
    # Obtener estudiantes
    estudiantes = Estudiante.objects.all().order_by('nombres_completos')
    if grado:
        estudiantes = estudiantes.filter(grado=grado)
    if paralelo:
        estudiantes = estudiantes.filter(paralelo=paralelo)
    
    # Obtener asignatura
    asignatura = None
    if asignatura_id:
        try:
            asignatura = Asignatura.objects.get(pk=asignatura_id)
        except Asignatura.DoesNotExist:
            asignatura = None
    
    # Obtener calificaciones
    calificaciones_data = {}
    if asignatura:
        calificaciones = Calificacion.objects.filter(
            estudiante__in=estudiantes,
            asignatura=asignatura,
            trimestre=trimestre
        ).select_related('estudiante')
        for cal in calificaciones:
            calificaciones_data[cal.estudiante.id_estudiante] = cal
    
    # Crear PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Título principal
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,
        spaceAfter=15,
        textColor=colors.HexColor('#1e40af')
    )
    
    elements.append(Paragraph("SISTEMA DE CALIFICACIONES - REPORTE PDF", title_style))
    
    # Información del curso
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=3
    )
    
    info_data = [
        [Paragraph(f"<b>GRADO:</b> {grado}", info_style),
         Paragraph(f"<b>PARALELO:</b> {paralelo if paralelo else 'Todos'}", info_style)],
        [Paragraph(f"<b>ASIGNATURA:</b> {asignatura.get_nombre_display() if asignatura else 'No especificada'}", info_style),
         Paragraph(f"<b>TRIMESTRE:</b> {dict(Calificacion.TRIMESTRE_CHOICES).get(int(trimestre), 'Primer')}", info_style)],
        [Paragraph(f"<b>TOTAL ESTUDIANTES:</b> {estudiantes.count()}", info_style),
         Paragraph(f"<b>FECHA:</b> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", info_style)],
    ]
    
    info_table = Table(info_data, colWidths=[4*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    
    # Tabla de calificaciones
    headers = ['#', 'ESTUDIANTE', 'CÉDULA', 'LEC.1', 'LEC.2', 'ACT.EXP.', 'PROY.INT.', 'EXAMEN', 'PROM.FOR.', 'PROM.SUM.', 'PROM.FINAL', 'ESTADO']
    
    data = [headers]
    
    for i, estudiante in enumerate(estudiantes, 1):
        calificacion = calificaciones_data.get(estudiante.id_estudiante)
        
        if calificacion:
            leccion1 = f"{calificacion.leccion1:.1f}" if calificacion.leccion1 > 0 else "-"
            leccion2 = f"{calificacion.leccion2:.1f}" if calificacion.leccion2 > 0 else "-"
            act_exp = f"{calificacion.actividad_experiencial:.1f}" if calificacion.actividad_experiencial > 0 else "-"
            proyecto = f"{calificacion.proyecto_interdisciplinar:.1f}" if calificacion.proyecto_interdisciplinar > 0 else "-"
            examen = f"{calificacion.examen:.1f}" if calificacion.examen > 0 else "-"
            prom_for = f"{calificacion.promedio_formativo:.2f}" if calificacion.promedio_formativo > 0 else "-"
            prom_sum = f"{calificacion.promedio_sumativo:.2f}" if calificacion.promedio_sumativo > 0 else "-"
            prom_final = f"{calificacion.promedio_final_100:.2f}" if calificacion.promedio_final_100 > 0 else "-"
            
            if calificacion.promedio_final_100 >= 7:
                estado = "APROBADO"
            elif calificacion.promedio_final_100 >= 5:
                estado = "SUPLETORIO"
            else:
                estado = "REPROBADO" if calificacion.promedio_final_100 > 0 else "SIN DATOS"
        else:
            leccion1 = leccion2 = act_exp = proyecto = examen = prom_for = prom_sum = prom_final = "-"
            estado = "SIN DATOS"
        
        data.append([
            str(i),
            estudiante.nombres_completos[:25],
            estudiante.cedula,
            leccion1,
            leccion2,
            act_exp,
            proyecto,
            examen,
            prom_for,
            prom_sum,
            prom_final,
            estado
        ])
    
    # Crear tabla
    table = Table(data, repeatRows=1)
    
    # Estilos de tabla
    table_style = TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        
        # Bordes y alineación
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (1, -1), 'LEFT'),
        
        # Colores según estado
        ('TEXTCOLOR', (11, 1), (11, -1), 
         lambda row, col, val: colors.green if val == 'APROBADO' 
                               else colors.orange if val == 'SUPLETORIO' 
                               else colors.red if val == 'REPROBADO' 
                               else colors.grey),
        ('FONTNAME', (11, 1), (11, -1), 'Helvetica-Bold'),
        
        # Alternar colores de filas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ])
    
    table.setStyle(table_style)
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Estadísticas
    estudiantes_con_datos = sum(1 for row in data[1:] if any(x != "-" for x in row[3:8]))
    estudiantes_aprobados = sum(1 for row in data[1:] if row[11] == "APROBADO")
    estudiantes_supletorio = sum(1 for row in data[1:] if row[11] == "SUPLETORIO")
    
    stats_text = f"""
    <b>ESTADÍSTICAS:</b> Total: {len(data)-1} | Con datos: {estudiantes_con_datos} | 
    Aprobados: {estudiantes_aprobados} | Supletorios: {estudiantes_supletorio} | 
    Sin datos: {len(data)-1 - estudiantes_con_datos}
    """
    elements.append(Paragraph(stats_text, info_style))
    
    # Pie de página
    elements.append(Spacer(1, 30))
    footer = Paragraph(
        f"<b>Sistema GESINFRA_WEB</b> | Reporte generado automáticamente | Página 1 de 1",
        ParagraphStyle('FooterStyle', parent=styles['Normal'], fontSize=8, alignment=1, textColor=colors.grey)
    )
    elements.append(footer)
    
    # Generar PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    # Crear respuesta
    response = HttpResponse(content_type='application/pdf')
    filename = f"calificaciones_{grado}_{paralelo}_T{trimestre}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)
    
    return response

# ========== VISTAS DE LISTAS ==========

@login_required 
def lista_calificaciones(request):
    """Lista de calificaciones para reportes por estudiante"""
    # Obtener parámetros de filtro
    grado = request.GET.get('grado', '')
    paralelo = request.GET.get('paralelo', '')
    trimestre = request.GET.get('trimestre', '')
    
    # Obtener TODOS los estudiantes (importante para la sidebar)
    estudiantes = Estudiante.objects.all().order_by('grado', 'paralelo', 'nombres_completos')
    
    # Obtener calificaciones con relaciones
    calificaciones = Calificacion.objects.all().select_related(
        'estudiante', 
        'asignatura'
    ).order_by('estudiante__nombres_completos', 'trimestre')
    
    # Aplicar filtros a calificaciones
    if grado:
        calificaciones = calificaciones.filter(estudiante__grado=grado)
    if paralelo:
        calificaciones = calificaciones.filter(estudiante__paralelo=paralelo)
    if trimestre:
        calificaciones = calificaciones.filter(trimestre=trimestre)
    
    # Definir grados organizados por nivel
    GRADOS_EGB_MEDIA = ['5EGB', '6EGB', '7EGB']
    GRADOS_EGB_SUPERIOR = ['8EGB', '9EGB', '10EGB']
    
    # Obtener grados disponibles de los estudiantes
    grados_disponibles = Estudiante.objects.values_list('grado', flat=True).distinct().order_by('grado')
    paralelos = Estudiante.objects.values_list('paralelo', flat=True).distinct().order_by('paralelo')
    
    # Organizar grados por nivel
    grados_media = [g for g in GRADOS_EGB_MEDIA if g in grados_disponibles]
    grados_superior = [g for g in GRADOS_EGB_SUPERIOR if g in grados_disponibles]
    
    context = {
        'calificaciones': calificaciones,
        'estudiantes': estudiantes,
        'grados_media': grados_media,
        'grados_superior': grados_superior,
        'paralelos': paralelos,
        'grado_filtro': grado,
        'paralelo_filtro': paralelo,
        'trimestre_filtro': trimestre,
        'total_calificaciones': calificaciones.count(),
    }
    
    return render(request, 'calificaciones/calificaciones/lista.html', context)

@login_required
def lista_estudiantes(request):
    """Lista de estudiantes"""
    estudiantes = Estudiante.objects.all().order_by('grado', 'paralelo', 'nombres_completos')
    
    return render(request, 'calificaciones/estudiantes/lista.html', {
        'estudiantes': estudiantes,
    })

@login_required
def lista_docentes(request):
    """Lista de docentes"""
    docentes = Docente.objects.all()
    
    return render(request, 'calificaciones/docentes/lista.html', {
        'docentes': docentes,
    })

@login_required
def lista_asignaturas(request):
    """Lista de asignaturas"""
    asignaturas = Asignatura.objects.all()
    
    return render(request, 'calificaciones/asignaturas/lista.html', {
        'asignaturas': asignaturas,
    })

# ========== VISTAS DE AGREGAR ==========

@login_required
def agregar_estudiante(request):
    """Agregar nuevo estudiante"""
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            estudiante = form.save()
            messages.success(request, f'✅ Estudiante "{estudiante.nombres_completos}" creado exitosamente!')
            return redirect('calificaciones:lista_estudiantes')
    else:
        form = EstudianteForm()
    
    return render(request, 'calificaciones/estudiantes/form.html', {'form': form})

@login_required
def agregar_docente(request):
    """Agregar nuevo docente"""
    if request.method == 'POST':
        form = DocenteForm(request.POST)
        if form.is_valid():
            docente = form.save()
            messages.success(request, f'✅ Docente "{docente.nombres_completos}" creado exitosamente!')
            return redirect('calificaciones:lista_docentes')
    else:
        form = DocenteForm()
    
    return render(request, 'calificaciones/docentes/form.html', {'form': form})

@login_required
def agregar_asignatura(request):
    """Agregar nueva asignatura"""
    if request.method == 'POST':
        form = AsignaturaForm(request.POST)
        if form.is_valid():
            asignatura = form.save()
            messages.success(request, f'✅ Asignatura "{asignatura.nombre}" creada exitosamente!')
            return redirect('calificaciones:lista_asignaturas')
    else:
        form = AsignaturaForm()
    
    return render(request, 'calificaciones/asignaturas/form.html', {'form': form})

@login_required
def agregar_calificacion(request):
    """Agregar nueva calificación"""
    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Calificación agregada exitosamente!')
            return redirect('calificaciones:lista_calificaciones')
    else:
        form = CalificacionForm()
    
    return render(request, 'calificaciones/calificaciones/form.html', {'form': form})

# ========== VISTAS DE EDITAR ==========

@login_required
def editar_estudiante(request, id_estudiante):
    """Editar estudiante"""
    estudiante = get_object_or_404(Estudiante, id_estudiante=id_estudiante)
    
    if request.method == 'POST':
        form = EstudianteForm(request.POST, instance=estudiante)
        if form.is_valid():
            estudiante = form.save()
            messages.success(request, f'✅ Estudiante "{estudiante.nombres_completos}" actualizado!')
            return redirect('calificaciones:lista_estudiantes')
    else:
        form = EstudianteForm(instance=estudiante)
    
    return render(request, 'calificaciones/estudiantes/form.html', {
        'form': form,
        'estudiante': estudiante
    })

@login_required
def editar_docente(request, id_docente):
    """Editar docente"""
    docente = get_object_or_404(Docente, id_docente=id_docente)
    
    if request.method == 'POST':
        form = DocenteForm(request.POST, instance=docente)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Docente "{docente.nombres_completos}" actualizado!')
            return redirect('calificaciones:lista_docentes')
    else:
        form = DocenteForm(instance=docente)
    
    return render(request, 'calificaciones/docentes/form.html', {'form': form})

@login_required
def editar_asignatura(request, id_asignatura):
    """Editar asignatura"""
    asignatura = get_object_or_404(Asignatura, id_asignatura=id_asignatura)
    
    if request.method == 'POST':
        form = AsignaturaForm(request.POST, instance=asignatura)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Asignatura "{asignatura.nombre}" actualizada!')
            return redirect('calificaciones:lista_asignaturas')
    else:
        form = AsignaturaForm(instance=asignatura)
    
    return render(request, 'calificaciones/asignaturas/form.html', {'form': form})

@login_required
def editar_calificacion(request, id_calificacion):
    """Editar calificación"""
    calificacion = get_object_or_404(Calificacion, id_calificacion=id_calificacion)
    
    if request.method == 'POST':
        form = CalificacionForm(request.POST, instance=calificacion)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Calificación actualizada!')
            return redirect('calificaciones:lista_calificaciones')
    else:
        form = CalificacionForm(instance=calificacion)
    
    return render(request, 'calificaciones/calificaciones/form.html', {'form': form})

# ========== VISTAS DE ELIMINAR ==========

@login_required
def eliminar_estudiante(request, id_estudiante):
    """Eliminar estudiante"""
    estudiante = get_object_or_404(Estudiante, id_estudiante=id_estudiante)
    
    if request.method == 'POST':
        nombre = estudiante.nombres_completos
        estudiante.delete()
        messages.success(request, f'✅ Estudiante "{nombre}" eliminado!')
        return redirect('calificaciones:lista_estudiantes')
    
    return render(request, 'calificaciones/estudiantes/confirmar_eliminar.html', {'estudiante': estudiante})

@login_required
def eliminar_docente(request, id_docente):
    """Eliminar docente"""
    docente = get_object_or_404(Docente, id_docente=id_docente)
    
    if request.method == 'POST':
        nombre = docente.nombres_completos
        docente.delete()
        messages.success(request, f'✅ Docente "{nombre}" eliminado!')
        return redirect('calificaciones:lista_docentes')
    
    return render(request, 'calificaciones/docentes/confirmar_eliminar.html', {'docente': docente})

@login_required
def eliminar_asignatura(request, id_asignatura):
    """Eliminar asignatura"""
    asignatura = get_object_or_404(Asignatura, id_asignatura=id_asignatura)
    
    if request.method == 'POST':
        nombre = asignatura.nombre
        asignatura.delete()
        messages.success(request, f'✅ Asignatura "{nombre}" eliminada!')
        return redirect('calificaciones:lista_asignaturas')
    
    return render(request, 'calificaciones/asignaturas/confirmar_eliminar.html', {'asignatura': asignatura})

@login_required
def eliminar_calificacion(request, id_calificacion):
    """Eliminar calificación"""
    calificacion = get_object_or_404(Calificacion, id_calificacion=id_calificacion)
    
    if request.method == 'POST':
        calificacion.delete()
        messages.success(request, '✅ Calificación eliminada!')
        return redirect('calificaciones:lista_calificaciones')
    
    return render(request, 'calificaciones/calificaciones/confirmar_eliminar.html', {'calificacion': calificacion})

# ========== BOLETAS POR TRIMESTRE ==========

@login_required
def boleta_estudiante_trimestre(request, estudiante_id, trimestre):
    """Boleta individual por estudiante y trimestre"""
    try:
        estudiante = get_object_or_404(Estudiante, id_estudiante=estudiante_id)
        
        # Obtener todas las asignaturas
        asignaturas = Asignatura.objects.all()
        
        # Obtener calificaciones del estudiante para el trimestre
        calificaciones = Calificacion.objects.filter(
            estudiante=estudiante,
            trimestre=trimestre
        ).select_related('asignatura')
        
        # Crear diccionario de calificaciones por asignatura
        calificaciones_dict = {cal.asignatura_id: cal for cal in calificaciones}
        
        # Preparar datos para la tabla
        datos_asignaturas = []
        suma_promedios_finales = 0
        asignaturas_con_notas = 0
        
        for asignatura in asignaturas:
            calificacion = calificaciones_dict.get(asignatura.id_asignatura)
            
            if calificacion and calificacion.promedio_final_100 > 0:
                # Usar los promedios ya calculados del modelo
                leccion1 = float(calificacion.leccion1) if calificacion.leccion1 > 0 else 0
                leccion2 = float(calificacion.leccion2) if calificacion.leccion2 > 0 else 0
                act_exp = float(calificacion.actividad_experiencial) if calificacion.actividad_experiencial > 0 else 0
                proyecto = float(calificacion.proyecto_interdisciplinar) if calificacion.proyecto_interdisciplinar > 0 else 0
                examen = float(calificacion.examen) if calificacion.examen > 0 else 0
                promedio_final = float(calificacion.promedio_final_100)
                
                # Estado
                if promedio_final >= 7:
                    estado = "APROBADO"
                    estado_color = "success"
                    estado_bg = "bg-success"
                elif promedio_final >= 5:
                    estado = "SUPLETORIO"
                    estado_color = "warning"
                    estado_bg = "bg-warning text-dark"
                else:
                    estado = "REPROBADO"
                    estado_color = "danger"
                    estado_bg = "bg-danger"
                
                datos_asignaturas.append({
                    'asignatura': asignatura,
                    'leccion1': leccion1,
                    'leccion2': leccion2,
                    'act_exp': act_exp,
                    'proyecto': proyecto,
                    'examen': examen,
                    'promedio_formativo': float(calificacion.promedio_formativo),
                    'promedio_sumativo': float(calificacion.promedio_sumativo),
                    'promedio_final': promedio_final,
                    'estado': estado,
                    'estado_color': estado_color,
                    'estado_bg': estado_bg
                })
                
                suma_promedios_finales += promedio_final
                asignaturas_con_notas += 1
            else:
                # Si no hay calificación
                datos_asignaturas.append({
                    'asignatura': asignatura,
                    'leccion1': 0,
                    'leccion2': 0,
                    'act_exp': 0,
                    'proyecto': 0,
                    'examen': 0,
                    'promedio_formativo': 0,
                    'promedio_sumativo': 0,
                    'promedio_final': 0,
                    'estado': "SIN DATOS",
                    'estado_color': "secondary",
                    'estado_bg': "bg-secondary"
                })
        
        # Calcular promedio general del trimestre
        promedio_general_trimestre = 0
        if asignaturas_con_notas > 0:
            promedio_general_trimestre = suma_promedios_finales / asignaturas_con_notas
        
        # Determinar color del promedio general
        if promedio_general_trimestre >= 7:
            promedio_color = "text-success"
            promedio_bg = "bg-success"
            promedio_estado = "APROBADO"
        elif promedio_general_trimestre >= 5:
            promedio_color = "text-warning"
            promedio_bg = "bg-warning text-dark"
            promedio_estado = "SUPLETORIO"
        elif promedio_general_trimestre > 0:
            promedio_color = "text-danger"
            promedio_bg = "bg-danger"
            promedio_estado = "REPROBADO"
        else:
            promedio_color = "text-secondary"
            promedio_bg = "bg-secondary"
            promedio_estado = "SIN DATOS"
        
        # Nombre del trimestre
        nombres_trimestres = {
            1: "PRIMER TRIMESTRE",
            2: "SEGUNDO TRIMESTRE",
            3: "TERCER TRIMESTRE"
        }
        nombre_trimestre = nombres_trimestres.get(trimestre, f"TRIMESTRE {trimestre}")
        
        context = {
            'estudiante': estudiante,
            'trimestre': trimestre,
            'nombre_trimestre': nombre_trimestre,
            'datos_asignaturas': datos_asignaturas,
            'promedio_general': round(promedio_general_trimestre, 2),
            'promedio_color': promedio_color,
            'promedio_bg': promedio_bg,
            'promedio_estado': promedio_estado,
            'asignaturas_con_notas': asignaturas_con_notas,
            'total_asignaturas': len(asignaturas),
            'fecha_actual': datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        
        return render(request, 'calificaciones/reportes/boleta_trimestre.html', context)
        
    except Estudiante.DoesNotExist:
        messages.error(request, 'Estudiante no encontrado')
        return redirect('calificaciones:lista_estudiantes')

@login_required
def generar_pdf_boleta_trimestre(request, estudiante_id, trimestre):
    """Generar PDF de la boleta por trimestre con diseño profesional"""
    try:
        estudiante = get_object_or_404(Estudiante, id_estudiante=estudiante_id)
        asignaturas = Asignatura.objects.all()
        
        # Obtener calificaciones
        calificaciones = Calificacion.objects.filter(
            estudiante=estudiante,
            trimestre=trimestre
        ).select_related('asignatura')
        
        calificaciones_dict = {cal.asignatura_id: cal for cal in calificaciones}
        
        # Preparar datos para el PDF
        datos_asignaturas = []
        suma_promedios_formativos = 0
        suma_promedios_sumativos = 0
        suma_promedios_finales = 0
        asignaturas_con_notas = 0
        
        for asignatura in asignaturas:
            calificacion = calificaciones_dict.get(asignatura.id_asignatura)
            
            if calificacion and calificacion.promedio_final_100 > 0:
                # Usar los promedios ya calculados del modelo
                leccion1 = float(calificacion.leccion1) if calificacion.leccion1 > 0 else 0
                leccion2 = float(calificacion.leccion2) if calificacion.leccion2 > 0 else 0
                act_exp = float(calificacion.actividad_experiencial) if calificacion.actividad_experiencial > 0 else 0
                proyecto = float(calificacion.proyecto_interdisciplinar) if calificacion.proyecto_interdisciplinar > 0 else 0
                examen = float(calificacion.examen) if calificacion.examen > 0 else 0
                
                # Calcular promedio formativo manualmente para mostrar la fórmula
                notas_formativas = [n for n in [leccion1, leccion2, act_exp] if n > 0]
                promedio_formativo = sum(notas_formativas) / len(notas_formativas) if notas_formativas else 0
                aporte_formativo = promedio_formativo * 0.7
                
                # Calcular promedio sumativo
                notas_sumativas = [n for n in [proyecto, examen] if n > 0]
                promedio_sumativo = sum(notas_sumativas) / len(notas_sumativas) if notas_sumativas else 0
                aporte_sumativo = promedio_sumativo * 0.3
                
                promedio_final = aporte_formativo + aporte_sumativo
                
                # Acumular para sumas finales
                suma_promedios_formativos += promedio_formativo
                suma_promedios_sumativos += promedio_sumativo
                suma_promedios_finales += promedio_final
                asignaturas_con_notas += 1
                
                # Estado con emojis para PDF
                if promedio_final >= 7:
                    estado = "✅ APROBADO"
                elif promedio_final >= 5:
                    estado = "⚠ SUPLETORIO"
                else:
                    estado = "❌ REPROBADO"
                
                datos_asignaturas.append([
                    asignatura.get_nombre_display(),
                    f"{leccion1:.1f}" if leccion1 > 0 else "-",
                    f"{leccion2:.1f}" if leccion2 > 0 else "-",
                    f"{act_exp:.1f}" if act_exp > 0 else "-",
                    f"{proyecto:.1f}" if proyecto > 0 else "-",
                    f"{examen:.1f}" if examen > 0 else "-",
                    f"{promedio_formativo:.2f}",
                    f"{aporte_formativo:.2f}",
                    f"{promedio_sumativo:.2f}",
                    f"{aporte_sumativo:.2f}",
                    f"{promedio_final:.2f}",
                    estado
                ])
            else:
                # Si no hay calificación
                datos_asignaturas.append([
                    asignatura.get_nombre_display(),
                    "-", "-", "-", "-", "-",
                    "0.00", "0.00", "0.00", "0.00", "0.00",
                    "📭 SIN DATOS"
                ])
        
        # Calcular promedios generales del trimestre
        promedio_general_formativas = suma_promedios_formativos / asignaturas_con_notas if asignaturas_con_notas > 0 else 0
        promedio_general_sumativas = suma_promedios_sumativos / asignaturas_con_notas if asignaturas_con_notas > 0 else 0
        promedio_general_final = suma_promedios_finales / asignaturas_con_notas if asignaturas_con_notas > 0 else 0
        
        # Nombre del trimestre
        nombres_trimestres = {
            1: "PRIMER TRIMESTRE",
            2: "SEGUNDO TRIMESTRE",
            3: "TERCER TRIMESTRE"
        }
        nombre_trimestre = nombres_trimestres.get(trimestre, f"TRIMESTRE {trimestre}")
        
        # Crear PDF
        buffer = BytesIO()
        
        # Configurar documento PDF con tamaño personalizado y márgenes
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm,
            leftMargin=1.5*cm,
            rightMargin=1.5*cm
        )
        elements = []
        
        # ========== ESTILOS PROFESIONALES ==========
        styles = getSampleStyleSheet()
        
        # Fuentes personalizadas (simuladas)
        styles.add(ParagraphStyle(
            name='TitleFont',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=colors.HexColor('#1a237e'),  # Azul oscuro profesional
            alignment=1,
            spaceAfter=20
        ))
        
        styles.add(ParagraphStyle(
            name='SubtitleFont',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor('#283593'),
            alignment=1,
            spaceAfter=15
        ))
        
        styles.add(ParagraphStyle(
            name='HeaderFont',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=colors.white
        ))
        
        styles.add(ParagraphStyle(
            name='DataFont',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8
        ))
        
        styles.add(ParagraphStyle(
            name='BoldDataFont',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8
        ))
        
        # ========== ENCABEZADO INSTITUCIONAL ==========
        elements.append(Paragraph(
            "<b>GESINFRA WEB - SISTEMA ACADÉMICO</b>",
            ParagraphStyle(
                name='InstitutionFont',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=10,
                textColor=colors.HexColor('#1565c0'),
                alignment=0,
                spaceAfter=5
            )
        ))
        
        elements.append(Paragraph(
            "Reporte Oficial de Calificaciones",
            ParagraphStyle(
                name='ReportTitle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=9,
                textColor=colors.HexColor('#424242'),
                alignment=0,
                spaceAfter=10
            )
        ))
        
        elements.append(Paragraph(
            "=" * 80,
            ParagraphStyle(
                name='Separator',
                parent=styles['Normal'],
                fontName='Courier',
                fontSize=6,
                alignment=0,
                spaceAfter=15
            )
        ))
        
        # ========== TÍTULO PRINCIPAL ==========
        elements.append(Paragraph(f"BOLETA DE CALIFICACIONES - {nombre_trimestre}", styles['TitleFont']))
        
        # ========== INFORMACIÓN DEL ESTUDIANTE CON DISEÑO MEJORADO ==========
        info_table_data = [
            [
                Paragraph(f"<b>ESTUDIANTE:</b>", styles['BoldDataFont']),
                Paragraph(f"{estudiante.nombres_completos}", styles['DataFont']),
                Paragraph(f"<b>CÉDULA:</b>", styles['BoldDataFont']),
                Paragraph(f"{estudiante.cedula}", styles['DataFont'])
            ],
            [
                Paragraph(f"<b>GRADO/PARALELO:</b>", styles['BoldDataFont']),
                Paragraph(f"{estudiante.get_grado_display()} - {estudiante.paralelo}", styles['DataFont']),
                Paragraph(f"<b>JORNADA:</b>", styles['BoldDataFont']),
                Paragraph(f"{estudiante.jornada}", styles['DataFont'])
            ],
            [
                Paragraph(f"<b>AÑO LECTIVO:</b>", styles['BoldDataFont']),
                Paragraph(f"{estudiante.anio_lectivo}", styles['DataFont']),
                Paragraph(f"<b>FECHA EMISIÓN:</b>", styles['BoldDataFont']),
                Paragraph(f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['DataFont'])
            ]
        ]
        
        info_table = Table(info_table_data, colWidths=[1.5*cm, 5*cm, 2*cm, 4*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (0, 0), (0, 0)),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 15))
        
        # ========== RESUMEN DEL TRIMESTRE CON DISEÑO MODERNO ==========
        # Determinar color del promedio final
        if promedio_general_final >= 7:
            color_promedio = colors.HexColor('#2e7d32')  # Verde
            estado_promedio = "✅ APROBADO"
        elif promedio_general_final >= 5:
            color_promedio = colors.HexColor('#f57c00')  # Naranja
            estado_promedio = "⚠ SUPLETORIO"
        else:
            color_promedio = colors.HexColor('#c62828')  # Rojo
            estado_promedio = "❌ REPROBADO"
        
        resumen_data = [
            [
                Paragraph("RESUMEN ACADÉMICO", 
                         ParagraphStyle(
                             name='ResumenTitle',
                             parent=styles['Normal'],
                             fontName='Helvetica-Bold',
                             fontSize=10,
                             textColor=colors.white,
                             alignment=1
                         ))
            ],
            [
                Paragraph("<b>PROMEDIO GENERAL:</b>", styles['BoldDataFont']),
                Paragraph(f"<font color='{color_promedio}'><b>{promedio_general_final:.2f}</b></font>", 
                         ParagraphStyle(
                             name='PromedioFinal',
                             parent=styles['Normal'],
                             fontName='Helvetica-Bold',
                             fontSize=12,
                             alignment=1
                         )),
                Paragraph(f"<b>{estado_promedio}</b>", 
                         ParagraphStyle(
                             name='EstadoFinal',
                             parent=styles['Normal'],
                             fontName='Helvetica-Bold',
                             fontSize=9,
                             textColor=color_promedio,
                             alignment=1
                         ))
            ],
            [
                Paragraph("<b>Suma Format.:</b>", styles['DataFont']),
                Paragraph(f"{suma_promedios_formativos:.2f}", styles['BoldDataFont']),
                Paragraph("<b>Prom. Format.:</b>", styles['DataFont']),
                Paragraph(f"{promedio_general_formativas:.2f}", styles['BoldDataFont'])
            ],
            [
                Paragraph("<b>Suma Sumat.:</b>", styles['DataFont']),
                Paragraph(f"{suma_promedios_sumativos:.2f}", styles['BoldDataFont']),
                Paragraph("<b>Prom. Sumat.:</b>", styles['DataFont']),
                Paragraph(f"{promedio_general_sumativas:.2f}", styles['BoldDataFont'])
            ],
            [
                Paragraph("<b>TOTAL ASIGNATURAS:</b>", styles['BoldDataFont']),
                Paragraph(f"{len(asignaturas)}", styles['DataFont']),
                Paragraph("<b>CON CALIFICACIONES:</b>", styles['BoldDataFont']),
                Paragraph(f"{asignaturas_con_notas}", styles['DataFont'])
            ]
        ]
        
        resumen_table = Table(resumen_data, colWidths=[3.5*cm, 3*cm, 3.5*cm, 3*cm])
        resumen_table.setStyle(TableStyle([
            # Fila de título
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#37474f')),
            ('SPAN', (0, 0), (-1, 0)),
            ('PADDING', (0, 0), (-1, 0), 8),
            
            # Fila del promedio general
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#eceff1')),
            ('SPAN', (1, 1), (2, 1)),
            ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
            ('PADDING', (0, 1), (-1, 1), 10),
            
            # Filas de datos
            ('PADDING', (0, 2), (-1, -1), 6),
            ('ALIGN', (1, 2), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 2), (3, -1), 'RIGHT'),
            ('VALIGN', (0, 2), (-1, -1), 'MIDDLE'),
            
            # Bordes
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#90a4ae')),
            ('INNERGRID', (0, 2), (-1, -1), 0.25, colors.HexColor('#cfd8dc')),
            
            # Líneas separadoras
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#37474f')),
            ('LINEBELOW', (0, 1), (-1, 1), 1, colors.HexColor('#b0bec5')),
        ]))
        
        elements.append(resumen_table)
        elements.append(Spacer(1, 20))
        
        # ========== TABLA PRINCIPAL DE CALIFICACIONES ==========
        # Encabezados con grupos claros
        headers = [
            ['ASIGNATURA', '', '', '', '', '', '', '', '', '', '', ''],
            ['', 'FORMATIVA (70%)', '', '', 'SUMATIVA (30%)', '', '', '', '', 'RESULTADO', '', ''],
            ['Nombre', 'Lec.1', 'Lec.2', 'Act.Exp.', 'Proy.', 'Exam.', 'Prom.F', 'Apor.F', 'Prom.S', 'Apor.S', 'PROM.FINAL', 'ESTADO']
        ]
        
        # Combinar encabezados con datos
        data = headers + datos_asignaturas
        
        # Añadir fila de TOTALES
        if asignaturas_con_notas > 0:
            data.append([
                Paragraph("<b>TOTALES:</b>", styles['BoldDataFont']),
                '', '', '', '', '',
                Paragraph(f"<b>{suma_promedios_formativos:.2f}</b>", styles['BoldDataFont']),
                Paragraph(f"<b>{(suma_promedios_formativos / asignaturas_con_notas * 0.7):.2f}</b>", styles['BoldDataFont']),
                Paragraph(f"<b>{suma_promedios_sumativos:.2f}</b>", styles['BoldDataFont']),
                Paragraph(f"<b>{(suma_promedios_sumativos / asignaturas_con_notas * 0.3):.2f}</b>", styles['BoldDataFont']),
                Paragraph(f"<b>{suma_promedios_finales:.2f}</b>", styles['BoldDataFont']),
                Paragraph(f"<b>{asignaturas_con_notas} asignaturas</b>", styles['BoldDataFont'])
            ])
        
        # Añadir fila de PROMEDIOS FINALES
        data.append([
            Paragraph("<b>PROMEDIOS FINALES:</b>", styles['BoldDataFont']),
            '', '', '', '', '',
            Paragraph(f"<b>{promedio_general_formativas:.2f}</b>", styles['BoldDataFont']),
            Paragraph(f"<b>{(promedio_general_formativas * 0.7):.2f}</b>", styles['BoldDataFont']),
            Paragraph(f"<b>{promedio_general_sumativas:.2f}</b>", styles['BoldDataFont']),
            Paragraph(f"<b>{(promedio_general_sumativas * 0.3):.2f}</b>", styles['BoldDataFont']),
            Paragraph(f"<font color='{color_promedio}'><b>{promedio_general_final:.2f}</b></font>", 
                     ParagraphStyle(
                         name='FinalAverage',
                         parent=styles['Normal'],
                         fontName='Helvetica-Bold',
                         fontSize=10,
                         textColor=color_promedio
                     )),
            Paragraph(f"<b>PROMEDIO TRIMESTRAL</b>", styles['BoldDataFont'])
        ])
        
        # Anchos de columnas optimizados
        col_widths = [
            3.5*cm,    # Asignatura
            0.8*cm,    # Lec.1
            0.8*cm,    # Lec.2
            0.8*cm,    # Act.Exp.
            0.8*cm,    # Proy.
            0.8*cm,    # Exam.
            1.0*cm,    # Prom.F
            1.0*cm,    # Apor.F
            1.0*cm,    # Prom.S
            1.0*cm,    # Apor.S
            1.2*cm,    # PROM.FINAL
            1.8*cm     # ESTADO
        ]
        
        table = Table(data, colWidths=col_widths, repeatRows=3)  # Repetir 3 filas de encabezado
        
        # ========== ESTILOS COMPLEJOS PARA LA TABLA ==========
        table_style = TableStyle([
            # ========== ENCABEZADOS PRINCIPALES ==========
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),  # Azul oscuro
            ('SPAN', (0, 0), (-1, 0)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('PADDING', (0, 0), (-1, 0), 8),
            
            # ========== SUB-ENCABEZADOS ==========
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#3949ab')),  # Azul medio
            ('SPAN', (0, 1), (0, 1)),  # Asignatura
            ('SPAN', (1, 1), (3, 1)),  # Formativa
            ('SPAN', (4, 1), (5, 1)),  # Sumativa
            ('SPAN', (6, 1), (7, 1)),  # Prom.F y Apor.F
            ('SPAN', (8, 1), (9, 1)),  # Prom.S y Apor.S
            ('SPAN', (10, 1), (10, 1)), # Resultado
            ('SPAN', (11, 1), (11, 1)), # Estado
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
            ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 9),
            ('PADDING', (0, 1), (-1, 1), 6),
            
            # ========== ENCABEZADOS DE COLUMNAS ==========
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#5c6bc0')),  # Azul claro
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.white),
            ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (-1, 2), 8),
            ('PADDING', (0, 2), (-1, 2), 4),
            
            # ========== BORDES GENERALES ==========
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#b0bec5')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#37474f')),
            
            # ========== ALINEACIÓN DE DATOS ==========
            ('ALIGN', (0, 3), (0, -1), 'LEFT'),  # Columna Asignatura
            ('ALIGN', (1, 3), (5, -1), 'CENTER'), # Notas individuales
            ('ALIGN', (6, 3), (10, -1), 'RIGHT'), # Promedios
            ('ALIGN', (11, 3), (11, -1), 'CENTER'), # Estado
            
            # ========== FUENTES Y TAMAÑOS ==========
            ('FONTNAME', (0, 3), (0, -1), 'Helvetica'),  # Asignaturas normal
            ('FONTSIZE', (0, 3), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # ========== COLORES POR RANGO DE NOTAS ==========
            # Formativa (Lec.1, Lec.2, Act.Exp.) - Verde
            ('TEXTCOLOR', (1, 3), (3, -3), 
             lambda r, c, v: colors.HexColor('#2e7d32') if v != '-' and float(v.replace('-', '0')) >= 7.0
             else colors.HexColor('#f57c00') if v != '-' and 5.0 <= float(v.replace('-', '0')) < 7.0
             else colors.HexColor('#c62828') if v != '-' and float(v.replace('-', '0')) < 5.0
             else colors.HexColor('#757575')),
            
            # Sumativa (Proy., Examen) - Azul
            ('TEXTCOLOR', (4, 3), (5, -3), 
             lambda r, c, v: colors.HexColor('#1565c0') if v != '-' and float(v.replace('-', '0')) >= 7.0
             else colors.HexColor('#0288d1') if v != '-' and 5.0 <= float(v.replace('-', '0')) < 7.0
             else colors.HexColor('#0277bd') if v != '-' and float(v.replace('-', '0')) < 5.0
             else colors.HexColor('#757575')),
            
            # ========== COLORES PARA PROMEDIOS FINALES ==========
            ('TEXTCOLOR', (10, 3), (10, -3), 
             lambda r, c, v: colors.HexColor('#2e7d32') if v != '0.00' and float(v) >= 7.0
             else colors.HexColor('#f57c00') if v != '0.00' and 5.0 <= float(v) < 7.0
             else colors.HexColor('#c62828') if v != '0.00' and float(v) < 5.0
             else colors.HexColor('#757575')),
            ('FONTNAME', (10, 3), (10, -3), 'Helvetica-Bold'),
            
            # ========== COLORES PARA ESTADOS ==========
            ('TEXTCOLOR', (11, 3), (11, -3), 
             lambda r, c, v: colors.HexColor('#2e7d32') if 'APROBADO' in v
             else colors.HexColor('#f57c00') if 'SUPLETORIO' in v
             else colors.HexColor('#c62828') if 'REPROBADO' in v
             else colors.HexColor('#757575')),
            ('FONTNAME', (11, 3), (11, -3), 'Helvetica'),
            ('FONTSIZE', (11, 3), (11, -3), 7),
            
            # ========== FILAS DE TOTALES Y PROMEDIOS ==========
            ('BACKGROUND', (0, -2), (-1, -2), colors.HexColor('#e8f5e9')),  # Verde claro para totales
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e3f2fd')),  # Azul claro para promedios
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -2), (-1, -1), 8),
            ('PADDING', (0, -2), (-1, -1), 6),
            
            # ========== ALTERNAR COLORES DE FILAS ==========
            ('ROWBACKGROUNDS', (0, 3), (-1, -3), 
             [colors.white, colors.HexColor('#fafafa')]),
            
            # ========== LÍNEAS SEPARADORAS ==========
            ('LINEABOVE', (0, -2), (-1, -2), 1, colors.HexColor('#81c784')),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#64b5f6')),
        ])
        
        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # ========== EXPLICACIÓN DE LA FÓRMULA ==========
        formula_style = ParagraphStyle(
            name='FormulaStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=colors.HexColor('#546e7a'),
            alignment=0,
            spaceBefore=10,
            spaceAfter=10
        )
        
        formula_text = f"""
        <b>FÓRMULA DE CÁLCULO:</b><br/>
        • <b>Promedio Formativo</b> = (Lec.1 + Lec.2 + Act.Exp.) ÷ 3<br/>
        • <b>Aporte Formativo</b> = Promedio Formativo × 0.70<br/>
        • <b>Promedio Sumativo</b> = (Proy. + Exam.) ÷ 2<br/>
        • <b>Aporte Sumativo</b> = Promedio Sumativo × 0.30<br/>
        • <b>Promedio Final</b> = Aporte Formativo + Aporte Sumativo<br/>
        • <b>Promedio Trimestral</b> = Suma de Promedios Finales ÷ Número de Asignaturas = {promedio_general_final:.2f}
        """
        
        elements.append(Paragraph(formula_text, formula_style))
        
        # ========== LEYENDA DE COLORES ==========
        legend_data = [
            [
                Paragraph("<b>LEYENDA DE COLORES:</b>", 
                         ParagraphStyle(
                             name='LegendTitle',
                             parent=styles['Normal'],
                             fontName='Helvetica-Bold',
                             fontSize=8,
                             textColor=colors.HexColor('#37474f')
                         ))
            ],
            [
                Paragraph("🟢 7.0 - 10.0: Excelente/Aprobado", styles['DataFont']),
                Paragraph("🟡 5.0 - 6.9: Regular/Supletorio", styles['DataFont']),
                Paragraph("🔴 0.0 - 4.9: Bajo/Reprobado", styles['DataFont'])
            ]
        ]
        
        legend_table = Table(legend_data, colWidths=[6*cm, 6*cm, 6*cm])
        legend_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
            ('SPAN', (0, 0), (-1, 0)),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('PADDING', (0, 0), (-1, 0), 4),
            ('PADDING', (0, 1), (-1, 1), 3),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(legend_table)
        elements.append(Spacer(1, 15))
        
        # ========== FIRMAS CON DISEÑO PROFESIONAL ==========
        firmas_style = ParagraphStyle(
            name='FirmasStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7,
            textColor=colors.HexColor('#546e7a'),
            alignment=1,
            spaceBefore=20
        )
        
        firmas_data = [
            ['', '', ''],
            ['_________________________', '_________________________', '_________________________'],
            ['<b>DOCENTE TITULAR</b>', '<b>COORDINADOR ACADÉMICO</b>', '<b>REPRESENTANTE LEGAL</b>'],
            ['Nombre y firma', 'Nombre, firma y sello', 'Nombre y firma']
        ]
        
        firmas_table = Table(firmas_data, colWidths=[5*cm, 5*cm, 5*cm])
        firmas_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, 1), 9),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (-1, 2), 8),
            ('FONTSIZE', (0, 3), (-1, 3), 7),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#757575')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(firmas_table)
        
        # ========== PIE DE PÁGINA ==========
        footer_style = ParagraphStyle(
            name='FooterStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=6,
            alignment=1,
            textColor=colors.HexColor('#78909c'),
            spaceBefore=20
        )
        
        footer_text = f"""
        <b>Documento generado electrónicamente por el Sistema GESINFRA WEB</b> | 
        Promedios calculados automáticamente según fórmula establecida | 
        Válido únicamente con firma y sello correspondientes | 
        Emisión: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}
        """
        
        elements.append(Paragraph(footer_text, footer_style))
        
        # ========== GENERAR PDF ==========
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        
        # Crear respuesta HTTP
        response = HttpResponse(content_type='application/pdf')
        filename = f"Boleta_T{trimestre}_{estudiante.cedula}_{estudiante.nombres_completos[:20]}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        print(f"Error generando PDF: {str(e)}")
        traceback.print_exc()
        
        # Crear un PDF de error simple
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Error generando reporte")
        p.setFont("Helvetica", 12)
        p.drawString(100, 730, f"Detalles: {str(e)}")
        p.showPage()
        p.save()
        
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="error_report.pdf"'
        response.write(pdf)
        
        return response

@login_required
def boleta_calificaciones(request):
    """Página para seleccionar estudiante y generar PDF"""
    estudiantes = Estudiante.objects.all().order_by('nombres_completos')
    
    return render(request, 'calificaciones/reportes/boleta.html', {
        'estudiantes': estudiantes,
    })

@login_required
def generar_reporte_pdf(request, estudiante_id):
    """Generar PDF de reporte de calificaciones por estudiante"""
    try:
        # Obtener el estudiante
        estudiante = Estudiante.objects.get(id_estudiante=estudiante_id)
        
        # Obtener todas las calificaciones del estudiante
        calificaciones = Calificacion.objects.filter(estudiante=estudiante).select_related('asignatura')
        
        # Crear buffer para PDF
        buffer = BytesIO()
        
        # Configurar documento PDF en horizontal
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Título del documento
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,
            spaceAfter=20,
            textColor=colors.HexColor('#2c3e50')
        )
        
        elements.append(Paragraph("REPORTE DE CALIFICACIONES", title_style))
        elements.append(Spacer(1, 10))
        
        # Información del estudiante
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=5
        )
        
        # Encabezado con información del estudiante
        info_html = f"""
        <b>ESTUDIANTE:</b> {estudiante.nombres_completos}<br/>
        <b>CÉDULA:</b> {estudiante.cedula}<br/>
        <b>GRADO/PARALELO:</b> {estudiante.grado} - {estudiante.paralelo}<br/>
        <b>AÑO LECTIVO:</b> {estudiante.anio_lectivo}<br/>
        <b>FECHA DE EMISIÓN:</b> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}
        """
        
        elements.append(Paragraph(info_html, info_style))
        elements.append(Spacer(1, 15))
        
        # Agrupar calificaciones por trimestre
        trimestres = {}
        for cal in calificaciones:
            if cal.trimestre not in trimestres:
                trimestres[cal.trimestre] = []
            trimestres[cal.trimestre].append(cal)
        
        # Para cada trimestre
        for trimestre_num in sorted(trimestres.keys()):
            trimestre_nombre = f"Trimestre {trimestre_num}"
            
            # Título del trimestre
            trimestre_style = ParagraphStyle(
                'TrimestreStyle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=10,
                textColor=colors.HexColor('#3498db')
            )
            
            elements.append(Paragraph(f"TRIMESTRE {trimestre_num}", trimestre_style))
            
            # Crear tabla de calificaciones para este trimestre
            data = [['ASIGNATURA', 'FORMATIVA', 'SUMATIVA', 'PROMEDIO FINAL', 'ESTADO']]
            
            for cal in trimestres[trimestre_num]:
                # Calcular promedios
                formativa = cal.aporte_formativo_70 if hasattr(cal, 'aporte_formativo_70') else 0
                sumativa = cal.aporte_sumativo_30 if hasattr(cal, 'aporte_sumativo_30') else 0
                promedio = cal.promedio_final_100 if hasattr(cal, 'promedio_final_100') else 0
                
                # Determinar estado
                if promedio >= 7:
                    estado = "APROBADO"
                    estado_color = colors.green
                elif promedio >= 5:
                    estado = "SUPLETORIO"
                    estado_color = colors.orange
                else:
                    estado = "REPROBADO"
                    estado_color = colors.red
                
                data.append([
                    cal.asignatura.nombre,
                    f"{formativa:.2f}",
                    f"{sumativa:.2f}",
                    f"{promedio:.2f}",
                    estado
                ])
            
            # Crear tabla
            table = Table(data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.5*inch, 1.2*inch])
            
            # Estilos de la tabla
            table.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                
                # Bordes
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ALIGN', (1, 1), (3, -1), 'CENTER'),
                
                # Alternar colores de filas
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                
                # Color de estado
                ('TEXTCOLOR', (4, 1), (4, -1), 
                 lambda row, col, val: colors.green if val == 'APROBADO' 
                               else colors.orange if val == 'SUPLETORIO' 
                               else colors.red),
                ('FONTNAME', (4, 1), (4, -1), 'Helvetica-Bold'),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 15))
        
        # Calcular estadísticas generales
        if calificaciones:
            promedios = []
            for cal in calificaciones:
                if hasattr(cal, 'promedio_final_100'):
                    promedio = cal.promedio_final_100
                    if promedio is not None:
                        promedios.append(promedio)
            
            if promedios:
                promedio_general = sum(promedios) / len(promedios)
                aprobadas = sum(1 for cal in calificaciones 
                              if hasattr(cal, 'promedio_final_100') and 
                              cal.promedio_final_100 >= 7)
                
                # Resumen final
                resumen_style = ParagraphStyle(
                    'ResumenStyle',
                    parent=styles['Normal'],
                    fontSize=12,
                    spaceBefore=20,
                    spaceAfter=10,
                    alignment=1
                )
                
                estado_final = "APROBADO" if promedio_general >= 7 else "REPROBADO"
                estado_color = colors.green if estado_final == "APROBADO" else colors.red
                
                resumen_html = f"""
                <b>RESUMEN ACADÉMICO:</b><br/>
                <b>Promedio General:</b> {promedio_general:.2f}<br/>
                <b>Asignaturas Registradas:</b> {len(calificaciones)}<br/>
                <b>Asignaturas Aprobadas:</b> {aprobadas}<br/>
                <b>Estado Académico:</b> <font color="{estado_color}"><b>{estado_final}</b></font>
                """
                
                elements.append(Paragraph(resumen_html, resumen_style))
        
        # Pie de página
        elements.append(Spacer(1, 30))
        footer = Paragraph(
            f"<b>Sistema GESINFRA_WEB</b> | Reporte generado automáticamente | Página 1 de 1",
            ParagraphStyle('FooterStyle', parent=styles['Normal'], fontSize=8, 
                          alignment=1, textColor=colors.grey)
        )
        elements.append(footer)
        
        # Generar PDF
        doc.build(elements)
        
        # Obtener el PDF del buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        # Crear respuesta HTTP
        response = HttpResponse(content_type='application/pdf')
        filename = f"reporte_calificaciones_{estudiante.cedula}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf)
        
        return response
        
    except Estudiante.DoesNotExist:
        return HttpResponse("Estudiante no encontrado", status=404)
    except Exception as e:
        print(f"Error generando PDF: {str(e)}")
        return HttpResponse(f"Error generando PDF: {str(e)}", status=500)

@login_required
def dashboard_estadisticas(request):
    """Dashboard de estadísticas"""
    return render(request, 'calificaciones/dashboard/estadisticas.html')

@login_required
def busqueda_avanzada(request):
    """Búsqueda avanzada"""
    return render(request, 'calificaciones/busqueda/avanzada.html')

# ========== AJAX ==========

@login_required
def guardar_calificaciones_masivo(request):
    """Guardar calificaciones masivas (AJAX)"""
    if request.method == 'POST':
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def generar_reporte_general_estudiantes(request):
    """Generar reporte general de todos los estudiantes"""
    # Obtener parámetros de filtro
    grado = request.GET.get('grado', '')
    paralelo = request.GET.get('paralelo', '')
    
    # Filtrar estudiantes
    estudiantes = Estudiante.objects.all().order_by('grado', 'paralelo', 'nombres_completos')
    if grado:
        estudiantes = estudiantes.filter(grado=grado)
    if paralelo:
        estudiantes = estudiantes.filter(paralelo=paralelo)
    
    # Crear CSV
    response = HttpResponse(content_type='text/csv')
    filename = f'reporte_estudiantes_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Encabezados
    writer.writerow(['ID', 'Nombres Completos', 'Cédula', 'Grado', 'Paralelo', 
                     'Edad', 'Sexo', 'Fecha Nacimiento', 'Nacionalidad', 
                     'Lugar Nacimiento', 'Jornada', 'Año Lectivo', 'Fecha Registro'])
    
    # Datos
    for estudiante in estudiantes:
        writer.writerow([
            estudiante.id_estudiante,
            estudiante.nombres_completos,
            estudiante.cedula,
            estudiante.grado,
            estudiante.paralelo,
            estudiante.edad,
            estudiante.get_sexo_display(),
            estudiante.fecha_nacimiento.strftime('%d/%m/%Y') if estudiante.fecha_nacimiento else '',
            estudiante.nacionalidad,
            estudiante.lugar_nacimiento,
            estudiante.jornada,
            estudiante.anio_lectivo,
            estudiante.fecha_registro.strftime('%d/%m/%Y %H:%M') if estudiante.fecha_registro else ''
        ])
    
    return response