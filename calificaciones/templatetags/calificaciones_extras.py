# calificaciones/templatetags/calificaciones_extras.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtener item de un diccionario usando filter"""
    return dictionary.get(key) 
