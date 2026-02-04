from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplica el valor por el argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        try:
            return value * arg
        except (ValueError, TypeError):
            return 0

@register.filter
def get_rating_text(value):
    """Convierte el número de calificación a texto"""
    ratings = {
        1: "Muy deficiente",
        2: "Deficiente",
        3: "Regular",
        4: "Bueno",
        5: "Excelente"
    }
    return ratings.get(value, "No calificado")

@register.filter
def get_level(value):
    """Obtiene el nivel textual basado en el promedio"""
    try:
        num = float(value)
        if num >= 4:
            return "Excelente"
        elif num >= 3:
            return "Bueno"
        elif num >= 2:
            return "Regular"
        else:
            return "Deficiente"
    except (ValueError, TypeError):
        return "Sin datos"
    