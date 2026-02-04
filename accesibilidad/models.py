from django.db import models

class InstitucionEducativa(models.Model):
    TIPO_CHOICES = [
        ('PUBLICA', 'Pública'),
        ('PRIVADA', 'Privada'),
        ('FISCOMISIONAL', 'Fiscomisional'),
        ('MUNICIPAL', 'Municipal'),
    ]
    
    nombre_institucion = models.CharField(max_length=200, verbose_name="Nombre de la Institución")
    codigo_amie = models.CharField(max_length=20, unique=True, verbose_name="Código AMIE")
    provincia = models.CharField(max_length=50, verbose_name="Provincia")
    canton = models.CharField(max_length=50, verbose_name="Cantón")
    direccion = models.TextField(verbose_name="Dirección")
    tipo_institucion = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Institución")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Institución Educativa"
        verbose_name_plural = "Instituciones Educativas"
        ordering = ['nombre_institucion']
    
    def __str__(self):
        return f"{self.nombre_institucion} ({self.codigo_amie})"

class EncuestaBarreras(models.Model):
    RESPUESTA_CHOICES = [
        ('SIEMPRE', 'Siempre'),
        ('CASI_SIEMPRE', 'Casi Siempre'),
        ('AVECES', 'A veces'),
        ('CASI_NUNCA', 'Casi Nunca'),
        ('NUNCA', 'Nunca'),
        ('NO_APLICA', 'No aplica'),
    ]
    def calcular_promedio_general(self):
        puntaje_fisicas = self.calcular_puntaje_fisicas()
        puntaje_tecnologicas = self.calcular_puntaje_tecnologicas()
        return (puntaje_fisicas + puntaje_tecnologicas) / 2
    
    # Puntuaciones en porcentaje (sobre 100)
    PUNTUACIONES = {
        'SIEMPRE': {'valor': 100, 'texto': 'Excelente', 'clase': 'bg-success'},
        'CASI_SIEMPRE': {'valor': 80, 'texto': 'Bueno', 'clase': 'bg-primary'},
        'AVECES': {'valor': 60, 'texto': 'Regular', 'clase': 'bg-warning'},
        'CASI_NUNCA': {'valor':40, 'texto': 'Deficiente', 'clase': 'bg-orange'},
        'NUNCA': {'valor': 20, 'texto': 'Muy Deficiente', 'clase': 'bg-danger'},
        'NO_APLICA': {'valor': 0, 'texto': 'No Aplica', 'clase': 'bg-secondary'},
    }
    
    institucion = models.ForeignKey(InstitucionEducativa, on_delete=models.CASCADE, verbose_name="Institución")
    fecha_encuesta = models.DateField('Fecha de Encuesta')
    encuestador = models.CharField(max_length=200, verbose_name="Nombre del Encuestador", blank=True, null=True)
    cargo_encuestador = models.CharField(max_length=100, verbose_name="Cargo del Encuestador", blank=True, null=True)
    
    # BARRERAS FÍSICAS (7 preguntas)
    p1_accesos = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="1. Los accesos principales al edificio son fáciles de usar", default='NO_APLICA')
    p2_pasillos = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="2. Los pasillos y aulas están libres de obstáculos", default='NO_APLICA')
    p3_rampas = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="3. Existen rampas de acceso adecuadas", default='NO_APLICA')
    p4_banos = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="4. Los baños son accesibles", default='NO_APLICA')
    p5_puertas = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="5. Las puertas tienen ancho adecuado", default='NO_APLICA')
    p6_senialetica = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="6. La señalética es adecuada", default='NO_APLICA')
    p7_iluminacion = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="7. La iluminación es adecuada", default='NO_APLICA')
    
    # BARRERAS TECNOLÓGICAS (7 preguntas)
    p8_equipos = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="8. La institución cuenta con equipos tecnológicos suficientes", default='NO_APLICA')
    p9_internet = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="9. La conexión a internet es estable", default='NO_APLICA')
    p10_software = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="10. Se dispone de software educativo accesible", default='NO_APLICA')
    p11_plataformas = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="11. Las plataformas virtuales son accesibles", default='NO_APLICA')
    p12_capacitacion = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="12. Hay capacitación regular en tecnología", default='NO_APLICA')
    p13_soporte = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="13. Existe soporte técnico adecuado", default='NO_APLICA')
    p14_recursos = models.CharField(max_length=20, choices=RESPUESTA_CHOICES, verbose_name="14. Los recursos digitales son accesibles", default='NO_APLICA')
    
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    recomendaciones = models.TextField(blank=True, null=True, verbose_name="Recomendaciones")
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Encuesta de Barreras"
        verbose_name_plural = "Encuestas de Barreras"
        ordering = ['-fecha_encuesta']
    
    def get_info_puntuacion(self, respuesta):
        """Retorna toda la información de una puntuación"""
        if respuesta in self.PUNTUACIONES:
            return self.PUNTUACIONES[respuesta]
        return {'valor': 0, 'texto': 'Sin calificar', 'clase': 'bg-light text-dark'}
    
    def get_puntuacion(self, respuesta):
        """Convierte respuesta textual a puntuación numérica"""
        puntuaciones = {
            'SIEMPRE': 100,
            'CASI_SIEMPRE': 80,
            'AVECES': 60,
            'CASI_NUNCA': 40,
            'NUNCA': 20,
            'NO_APLICA': 0,
        }
        return puntuaciones.get(respuesta, 0)
    
    def get_promedio_fisico_calculado(self):
        """Calcula promedio de accesibilidad física"""
        preguntas_fisicas = [
            self.p1_accesos,
            self.p2_pasillos,
            self.p3_rampas,
            self.p4_banos,
            self.p5_puertas,
            self.p6_senialetica,
            self.p7_iluminacion,
        ]
        
        puntuaciones = []
        for respuesta in preguntas_fisicas:
            puntuacion = self.get_puntuacion(respuesta)
            if puntuacion > 0:  # Excluir NO_APLICA (0)
                puntuaciones.append(puntuacion)
        
        return sum(puntuaciones) / len(puntuaciones) if puntuaciones else 0
    
    def get_promedio_tecnologico_calculado(self):
        """Calcula promedio de accesibilidad tecnológica"""
        preguntas_tecno = [
            self.p8_equipos,
            self.p9_internet,
            self.p10_software,
            self.p11_plataformas,
            self.p12_capacitacion,
            self.p13_soporte,
            self.p14_recursos,
        ]
        
        puntuaciones = []
        for respuesta in preguntas_tecno:
            puntuacion = self.get_puntuacion(respuesta)
            if puntuacion > 0:  # Excluir NO_APLICA (0)
                puntuaciones.append(puntuacion)
        
        return sum(puntuaciones) / len(puntuaciones) if puntuaciones else 0
    
    def get_promedio_general_calculado(self):
        """Calcula promedio general"""
        fisico = self.get_promedio_fisico_calculado()
        tecnologico = self.get_promedio_tecnologico_calculado()
        
        # Promedio de ambos grupos
        return (fisico + tecnologico) / 2
    
    def __str__(self):
        return f"Encuesta {self.institucion} - {self.fecha_encuesta}"