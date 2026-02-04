# calificaciones/templatetags/dict_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtiene un item de un diccionario por clave"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def get_item_int(dictionary, key):
    """Obtiene un item de un diccionario por clave (int)"""
    if dictionary is None:
        return None
    return dictionary.get(int(key))