# accesibilidad/templatetags/form_tags.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Filtro para obtener valores de diccionario usando claves dinámicas"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.simple_tag
def render_field(field, css_class='form-control'):
    """Renderiza un campo de formulario con clases personalizadas"""
    return field.as_widget(attrs={'class': css_class})

@register.filter
def add_class(field, css_class):
    """Agrega una clase CSS a un campo de formulario"""
    return field.as_widget(attrs={'class': css_class})