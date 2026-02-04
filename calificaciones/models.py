# models.py - VERSIÓN COMPLETA Y CORREGIDA
# models.py
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal, ROUND_HALF_UP

class Estudiante(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    
    GRADO_CHOICES = [
        ('5EGB', '5.º de EGB'),
        ('6EGB', '6.º de EGB'),
        ('7EGB', '7.º de EGB'),
        ('8EGB', '8.º de EGB'),
        ('9EGB', '9.º de EGB'),
        ('10EGB', '10.º de EGB'),
        ('1BGU', '1.º de BGU'),
        ('2BGU', '2.º de BGU'),
        ('3BGU', '3.º de BGU'),
    ]
    
    PARALELO_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    ]
    
    JORNADA_CHOICES = [
        ('MATUTINA', 'Matutina'),
        ('VESPERTINA', 'Vespertina'),
        ('NOCTURNA', 'Nocturna'),
    ]
    
    id_estudiante = models.AutoField(primary_key=True)
    nombres_completos = models.CharField(max_length=200, verbose_name="Nombres Completos")
    cedula = models.CharField(max_length=20, unique=True, verbose_name="Cédula")
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    edad = models.IntegerField(verbose_name="Edad")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name="Sexo")
    nacionalidad = models.CharField(max_length=50, verbose_name="Nacionalidad")
    lugar_nacimiento = models.CharField(max_length=100, verbose_name="Lugar de Nacimiento")
    
    # Datos académicos
    grado = models.CharField(max_length=10, choices=GRADO_CHOICES, verbose_name="Grado")
    paralelo = models.CharField(max_length=1, choices=PARALELO_CHOICES, verbose_name="Paralelo")
    jornada = models.CharField(max_length=15, choices=JORNADA_CHOICES, verbose_name="Jornada")
    anio_lectivo = models.CharField(max_length=20, verbose_name="Año lectivo", help_text="Ejemplo: 2024-2025")
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nombres_completos']
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
    
    def __str__(self):
        return f"{self.nombres_completos} - {self.get_grado_display()} {self.paralelo}"

class Docente(models.Model):
    id_docente = models.AutoField(primary_key=True)
    nombres_completos = models.CharField(max_length=200, verbose_name="Nombres Completos")
    cedula = models.CharField(max_length=20, unique=True, verbose_name="Cédula")
    correo = models.EmailField(verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")
    
    class Meta:
        verbose_name = "Docente"
        verbose_name_plural = "Docentes"
    
    def __str__(self):
        return self.nombres_completos

class Asignatura(models.Model):
    ASIGNATURA_CHOICES = [
        ('LENGUA', 'Lengua y Literatura'),
        ('MATEMATICA', 'Matemática'),
        ('CIENCIAS', 'Ciencias Naturales'),
        ('SOCIALES', 'Estudios Sociales'),
        ('ARTISTICA', 'Educación Cultural y Artística'),
        ('FISICA', 'Educación Física'),
        ('INGLES', 'Lengua Extranjera (Inglés)'),
        ('COMPUTACION', 'Computación'),
        ('EMPRENDIMIENTO', 'Emprendimiento y Gestión'),
    ]
    
    id_asignatura = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, choices=ASIGNATURA_CHOICES, verbose_name="Asignatura")
    docente = models.ForeignKey(Docente, on_delete=models.SET_NULL, null=True, blank=True, 
                               verbose_name="Docente", related_name='asignaturas')
    horas_semanales = models.IntegerField(default=5, verbose_name="Horas Semanales")
    
    class Meta:
        verbose_name = "Asignatura"
        verbose_name_plural = "Asignaturas"
    
    def __str__(self):
        return self.get_nombre_display()

class Calificacion(models.Model):
    TRIMESTRE_CHOICES = [
        (1, 'Primer Trimestre'),
        (2, 'Segundo Trimestre'),
        (3, 'Tercer Trimestre'),
    ]
    
    id_calificacion = models.AutoField(primary_key=True)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, 
                                  related_name='calificaciones', verbose_name="Estudiante")
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, 
                                  verbose_name="Asignatura", related_name='calificaciones')
    trimestre = models.IntegerField(choices=TRIMESTRE_CHOICES, verbose_name="Trimestre")
    
    # Evaluación formativa
    leccion1 = models.DecimalField(max_digits=4, decimal_places=2, default=0, 
                                  verbose_name="Lección 1 (0-10)")
    leccion2 = models.DecimalField(max_digits=4, decimal_places=2, default=0, 
                                  verbose_name="Lección 2 (0-10)")
    actividad_experiencial = models.DecimalField(max_digits=4, decimal_places=2, default=0, 
                                                verbose_name="Actividad Experiencial (0-10)")
    
    # Campos calculados automáticamente
    promedio_formativo = models.DecimalField(max_digits=4, decimal_places=2, editable=False, 
                                            default=0, verbose_name="Promedio Formativo")
    aporte_formativo_70 = models.DecimalField(max_digits=4, decimal_places=2, editable=False, 
                                             default=0, verbose_name="Aporte Formativo (70%)")
    
    # Evaluación sumativa
    proyecto_interdisciplinar = models.DecimalField(max_digits=4, decimal_places=2, default=0, 
                                                   verbose_name="Proyecto Interdisciplinar (0-10)")
    examen = models.DecimalField(max_digits=4, decimal_places=2, default=0, 
                                verbose_name="Examen (0-10)")
    
    # Campos calculados automáticamente
    promedio_sumativo = models.DecimalField(max_digits=4, decimal_places=2, editable=False, 
                                           default=0, verbose_name="Promedio Sumativo")
    aporte_sumativo_30 = models.DecimalField(max_digits=4, decimal_places=2, editable=False, 
                                            default=0, verbose_name="Aporte Sumativo (30%)")
    
    # Resultado final
    promedio_final_100 = models.DecimalField(max_digits=4, decimal_places=2, editable=False, 
                                            default=0, verbose_name="Promedio Final")
    
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['estudiante', 'asignatura', 'trimestre']
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
        unique_together = ['estudiante', 'asignatura', 'trimestre']
    
    def calcular_promedios(self):
        """Calcular todos los promedios automáticamente"""
        
        self.leccion1 = Decimal(str(self.leccion1))
        self.leccion2 = Decimal(str(self.leccion2))
        self.actividad_experiencial = Decimal(str(self.actividad_experiencial))
        self.proyecto_interdisciplinar = Decimal(str(self.proyecto_interdisciplinar))
        self.examen = Decimal(str(self.examen))
        
        # ========== CÁLCULO FORMATIVO ==========
        notas_formativas = [self.leccion1, self.leccion2, self.actividad_experiencial]
        notas_formativas_validas = [n for n in notas_formativas if n > Decimal('0')]
        
        if len(notas_formativas_validas) > 0:
            suma_formativo = sum(notas_formativas_validas)
            self.promedio_formativo = (suma_formativo / Decimal(len(notas_formativas_validas))).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        else:
            self.promedio_formativo = Decimal('0.00')
        
        # Aporte formativo (70%)
        self.aporte_formativo_70 = (self.promedio_formativo * Decimal('0.70')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # ========== CÁLCULO SUMATIVO ==========
        notas_sumativas = [self.proyecto_interdisciplinar, self.examen]
        notas_sumativas_validas = [n for n in notas_sumativas if n > Decimal('0')]
        
        if len(notas_sumativas_validas) > 0:
            suma_sumativo = sum(notas_sumativas_validas)
            self.promedio_sumativo = (suma_sumativo / Decimal(len(notas_sumativas_validas))).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        else:
            self.promedio_sumativo = Decimal('0.00')
        
        # Aporte sumativo (30%)
        self.aporte_sumativo_30 = (self.promedio_sumativo * Decimal('0.30')).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # ========== PROMEDIO FINAL ==========
        self.promedio_final_100 = (self.aporte_formativo_70 + self.aporte_sumativo_30).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
    
    def save(self, *args, **kwargs):
        """Sobreescribir save para calcular promedios automáticamente"""
        self.calcular_promedios()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.estudiante} - {self.asignatura} - T{self.trimestre}: {self.promedio_final_100}"