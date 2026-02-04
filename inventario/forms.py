from django import forms
from .models import Equipo, Ubicacion, AsignacionEquipo, Mantenimiento

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = '__all__'
        widgets = {
            'anio_adquisicion': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2000',
                'max': '2025'
            }),
            'costo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'codigo_inventario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: LAB-COMP-001'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de serie único'
            }),
        }

class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento
        exclude = ['usuario']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'proximo_mantenimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del problema o mantenimiento...'
            }),
            'actividades_realizadas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Actividades realizadas durante el mantenimiento...'
            }),
            'repuestos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Repuestos utilizados...'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
            'costo_mantenimiento': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
        }