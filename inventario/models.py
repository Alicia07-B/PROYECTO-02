from django.db import models
from django.contrib.auth.models import User

class Equipo(models.Model):
    ESTADO_CHOICES = [
        ('OPERATIVO', 'Operativo'),
        ('MANTENIMIENTO', 'En Mantenimiento'),
        ('DAÑADO', 'Dañado'),
        ('BAJA', 'Dado de Baja'),
    ]
    
    CONDICION_CHOICES = [
        ('EXCELENTE', 'Excelente'),
        ('BUENO', 'Bueno'),
        ('REGULAR', 'Regular'),
        ('MALO', 'Malo'),
    ]
    
    TIPO_CHOICES = [
        ('COMPUTADORA', 'Computadora'),
        ('LAPTOP', 'Laptop'),
        ('IMPRESORA', 'Impresora'),
        ('PROYECTOR', 'Proyector'),
        ('TABLET', 'Tablet'),
        ('SERVER', 'Servidor'),
        ('SWITCH', 'Switch'),
        ('ROUTER', 'Router'),
        ('MONITOR', 'Monitor'),
        ('TELEVISOR', 'Televisor'),
    ]
    
    id_equipo = models.AutoField(primary_key=True)
    codigo_inventario = models.CharField(max_length=50, unique=True, verbose_name="Código de Inventario")
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, verbose_name="Tipo de Equipo")
    marca = models.CharField(max_length=100, verbose_name="Marca")
    modelo = models.CharField(max_length=100, verbose_name="Modelo")
    numero_serie = models.CharField(max_length=100, unique=True, verbose_name="Número de Serie")
    anio_adquisicion = models.IntegerField(verbose_name="Año de Adquisición")
    costo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, verbose_name="Estado")
    condicion_fisica = models.CharField(max_length=20, choices=CONDICION_CHOICES, verbose_name="Condición Física")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ['codigo_inventario']
    
    def __str__(self):
        return f"{self.tipo} - {self.marca} {self.modelo} ({self.codigo_inventario})"

class Ubicacion(models.Model):
    id_ubicacion = models.AutoField(primary_key=True)
    area = models.CharField(max_length=100, verbose_name="Área")
    aula_laboratorio = models.CharField(max_length=100, verbose_name="Aula/Laboratorio")
    piso = models.CharField(max_length=20, blank=True, null=True, verbose_name="Piso")
    edificio = models.CharField(max_length=50, blank=True, null=True, verbose_name="Edificio")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
        ordering = ['area', 'aula_laboratorio']
    
    def __str__(self):
        return f"{self.area} - {self.aula_laboratorio}"

class AsignacionEquipo(models.Model):
    equipo = models.OneToOneField(Equipo, on_delete=models.CASCADE, verbose_name="Equipo")
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, verbose_name="Ubicación")
    fecha_asignacion = models.DateField(auto_now_add=True, verbose_name="Fecha de Asignación")
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Responsable")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    
    class Meta:
        verbose_name = "Asignación de Equipo"
        verbose_name_plural = "Asignaciones de Equipos"
    
    def __str__(self):
        return f"{self.equipo} → {self.ubicacion}"

class Mantenimiento(models.Model):
    TIPO_CHOICES = [
        ('PREVENTIVO', 'Preventivo'),
        ('CORRECTIVO', 'Correctivo'),
        ('PREDICTIVO', 'Predictivo'),
        ('CALIBRACION', 'Calibración'),
    ]
    
    id_mantenimiento = models.AutoField(primary_key=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, verbose_name="Equipo")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Usuario")
    fecha = models.DateField(verbose_name="Fecha de Mantenimiento")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Mantenimiento")
    descripcion = models.TextField(verbose_name="Descripción")
    actividades_realizadas = models.TextField(verbose_name="Actividades Realizadas")
    repuestos = models.TextField(blank=True, null=True, verbose_name="Repuestos Utilizados")
    costo_mantenimiento = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Costo de Mantenimiento")
    estado_posterior = models.CharField(max_length=50, verbose_name="Estado Posterior")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    proximo_mantenimiento = models.DateField(blank=True, null=True, verbose_name="Próximo Mantenimiento")
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.equipo} - {self.tipo} - {self.fecha}"