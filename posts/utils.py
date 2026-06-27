# NUEVO: Utilidades para APIs
from django.http import JsonResponse
from functools import wraps

def api_required(view_func):
    """
    Decorador para forzar que una vista solo acepte peticiones API.
    Verifica que el header Accept contenga application/json.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        accept_header = request.META.get('HTTP_ACCEPT', '')
        if 'application/json' not in accept_header:
            return JsonResponse(
                {'error': 'Esta URL solo acepta peticiones API con Accept: application/json'},
                status=406
            )
        return view_func(request, *args, **kwargs)
    return wrapper

def api_response(data, status=200):
    """
    Helper para respuestas API estandarizadas.
    """
    return JsonResponse(data, status=status)

def api_error(message, status=400):
    """
    Helper para errores API estandarizados.
    """
    return JsonResponse({'error': message}, status=status)