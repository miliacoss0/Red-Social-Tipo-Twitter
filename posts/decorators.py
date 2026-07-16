from django.core.cache import cache
from functools import wraps
from django.conf import settings

def cache_page_timeout(timeout=settings.CACHE_TTL):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # generar una clave de caché basada en la url y el usuario
            user_id = request.user.id if request.user.is_authenticated else 'anon'
            cache_key = f"view_{request.path}_{user_id}"
            
            # intentar obtener del caché
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response
            
            # si no está en caché, ejecutar la vista
            response = view_func(request, *args, **kwargs)
            
            # guardar en caché solo si es una respuesta exitosa (200)
            if response.status_code == 200:
                cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator


def invalidar_cache_usuario(usuario_id):
    from django.core.cache import cache
    
    # buscar y eliminar todas las claves que contengan el ID del usuario
    cache.delete_pattern(f"*{usuario_id}*")
    
    # también invalidar el feed general
    cache.delete_pattern("*feed*")
    cache.delete_pattern("*api_feed*")