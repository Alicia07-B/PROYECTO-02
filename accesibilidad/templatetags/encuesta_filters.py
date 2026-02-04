from django import template

register = template.Library()

@register.filter
def mostrar_puntuacion(respuesta):
    """Muestra la puntuación y texto según la respuesta"""
    puntuaciones = {
        'SIEMPRE': {
            'puntuacion': '100/100',
            'texto': 'Excelente',
            'clase': 'bg-success'
        },
        'CASI_SIEMPRE': {
            'puntuacion': '80/100',
            'texto': 'Bueno',
            'clase': 'bg-primary'
        },
        'AVECES': {
            'puntuacion': '60/100',
            'texto': 'Regular',
            'clase': 'bg-warning'
        },
        'CASI_NUNCA': {
            'puntuacion': '40/100',
            'texto': 'Deficiente',
            'clase': 'bg-orange'
        },
        'NUNCA': {
            'puntuacion': '20/100',
            'texto': 'Muy Deficiente',
            'clase': 'bg-danger'
        },
        'NO_APLICA': {
            'puntuacion': 'N/A',
            'texto': 'No Aplica',
            'clase': 'bg-secondary'
        },
    }
    
    return puntuaciones.get(respuesta, {
        'puntuacion': '-/-',
        'texto': 'Sin calificar',
        'clase': 'bg-light text-dark'
    })
