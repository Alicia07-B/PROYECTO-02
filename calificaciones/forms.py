# calificaciones/forms.py
from django import forms
from .models import Estudiante, Docente, Asignatura, Calificacion

class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': 'required'
            }),
            'nombres_completos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese nombres completos',
                'required': 'required'
            }),
            'cedula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese número de cédula',
                'required': 'required'
            }),
            'edad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '5',
                'max': '25',
                'required': 'required'
            }),
            'sexo': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'nacionalidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Ecuatoriana'
            }),
            'lugar_nacimiento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Guayaquil, Guayas'
            }),
            'grado': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'paralelo': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'jornada': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'anio_lectivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '2024-2025',
                'required': 'required'
            }),
        }
        labels = {
            'grado': 'Grado',
            'paralelo': 'Paralelo',
            'jornada': 'Jornada',
            'anio_lectivo': 'Año lectivo',
        }

class DocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = '__all__'
        widgets = {
            'nombres_completos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese nombres completos',
                'required': 'required'
            }),
            'cedula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese número de cédula',
                'required': 'required'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@email.com',
                'required': 'required'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0999999999'
            }),
        }

class AsignaturaForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        fields = '__all__'
        widgets = {
            'nombre': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'docente': forms.Select(attrs={
                'class': 'form-control'
            }),
            'horas_semanales': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10'
            }),
        }

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = '__all__'
        widgets = {
            'estudiante': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'asignatura': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'trimestre': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'leccion1': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '10',
                'placeholder': '0-10'
            }),
            'leccion2': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '10',
                'placeholder': '0-10'
            }),
            'actividad_experiencial': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '10',
                'placeholder': '0-10'
            }),
            'proyecto_interdisciplinar': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '10',
                'placeholder': '0-10'
            }),
            'examen': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '10',
                'placeholder': '0-10'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
        }