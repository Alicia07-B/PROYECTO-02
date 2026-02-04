# Crea esta carpeta y archivo
# accesibilidad/templatetags/form_tags.py

from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Obtener un valor de un diccionario usando una clave."""
    return dictionary.get(key)