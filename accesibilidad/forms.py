# accesibilidad/forms.py - VERSIÓN CORREGIDA
from django import forms
from .models import InstitucionEducativa, EncuestaBarreras

class InstitucionForm(forms.ModelForm):
    class Meta:
        model = InstitucionEducativa
        fields = ['nombre_institucion', 'codigo_amie', 'provincia', 'canton', 
                 'direccion', 'tipo_institucion', 'telefono', 'email']
        
        widgets = {
            'nombre_institucion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo de la institución'}),
            'codigo_amie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 17H00123'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pichincha'}),
            'canton': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Quito'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
            'tipo_institucion': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 022222222'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'institucion@educacion.gob.ec'}),
        }
        
        labels = {
            'nombre_institucion': 'Nombre de la Institución',
            'codigo_amie': 'Código AMIE',
            'provincia': 'Provincia',
            'canton': 'Cantón',
            'direccion': 'Dirección',
            'tipo_institucion': 'Tipo de Institución',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
        }

# FORMULARIO MANUAL PARA LA ENCUESTA (NO usar ModelForm)
class EncuestaBarrerasForm(forms.Form):
    # Información general
    fecha_encuesta = forms.DateField(
        label='Fecha de Encuesta',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    
    encuestador = forms.CharField(
        label='Nombre del Encuestador',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del evaluador'}),
        required=False,
        max_length=200
    )
    
    cargo_encuestador = forms.CharField(
        label='Cargo del Encuestador',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo del evaluador'}),
        required=False,
        max_length=100
    )
    
    # Opciones de respuesta
    OPCIONES = [
        ('', 'Seleccione...'),
        ('SIEMPRE', 'Siempre'),
        ('CASI_SIEMPRE', 'Casi Siempre'),
        ('AVECES', 'A veces'),
        ('CASI_NUNCA', 'Casi Nunca'),
        ('NUNCA', 'Nunca'),
        ('NO_APLICA', 'No aplica'),
    ]
    
    # Barreras Físicas (7 preguntas)
    p1_accesos = forms.ChoiceField(
        label='1. Los accesos principales al edificio (puertas, rampas) son fáciles de usar',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    p2_pasillos = forms.ChoiceField(
        label='2. Los pasillos, aulas y espacios comunes están libres de obstáculos',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    p3_rampas = forms.ChoiceField(
        label='3. Existen y están disponibles rampas o elevadores',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    p4_banos = forms.ChoiceField(
        label='4. Los baños son accesibles, cuentan con señales claras',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    p5_puertas = forms.ChoiceField(
        label='5. Las aulas tienen una iluminación y ventilación adecuadas',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    p6_senialetica = forms.ChoiceField(
        label='6. La señalización (letreros, pictogramas) es clara',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    p7_iluminacion = forms.ChoiceField(
        label='7. El mobiliario (sillas, mesas) es ajustable o adecuado',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    # Barreras Tecnológicas (7 preguntas)
    p8_equipos = forms.ChoiceField(
        label='8. La institución cuenta con equipos tecnológicos suficientes',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    p9_internet = forms.ChoiceField(
        label='9. La conexión a internet es estable, rápida y accesible',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    p10_software = forms.ChoiceField(
        label='10. Las plataformas y software educativos son accesibles',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    p11_plataformas = forms.ChoiceField(
        label='11. Los docentes reciben capacitación en tecnologías accesibles',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    p12_capacitacion = forms.ChoiceField(
        label='12. Los estudiantes cuentan con tecnología de asistencia adecuada',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    p13_soporte = forms.ChoiceField(
        label='13. Existe soporte técnico adecuado',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    p14_recursos = forms.ChoiceField(
        label='14. Los recursos digitales educativos son accesibles',
        choices=OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    # Observaciones
    observaciones = forms.CharField(
        label='Observaciones',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones generales...'}),
        required=False
    )
    
    recomendaciones = forms.CharField(
        label='Recomendaciones',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Recomendaciones para mejorar...'}),
        required=False
    )