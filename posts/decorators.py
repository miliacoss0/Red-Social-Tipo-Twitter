from django.core.cache import cache
from functools import wraps
from django.conf import settings
import hashlib

def cache_page_timeout(timeout=settings.CACHE_TTL):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Solo cachear peticiones GET
            if request.method != 'GET':
                return view_func(request, *args, **kwargs)
            user_id = request.user.id if request.user.is_authenticated else 'anon'
            key_parts = [
                request.path,
                str(user_id),
                str(sorted(request.GET.items())),
                str(args),
                str(sorted(kwargs.items()))
            ]
            cache_key = f"view_{hashlib.md5(''.join(key_parts).encode()).hexdigest()}"
            
            # intentar obtener del caché
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response
            
            response = view_func(request, *args, **kwargs)
            
            # guardar en caché solo si es exitoso
            if response.status_code == 200:
                cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator

def invalidar_cache_usuario(usuario_id):
    """Invalidar todas las entradas de caché relacionadas con un usuario"""
    from django.core.cache import cache
    
    # Limpiar caché del feed y API
    cache.delete_pattern("*feed*")
    cache.delete_pattern("*api_feed*")
    
    # Limpiar caché de mensajes
    cache.delete_pattern("*mensajes*")
    cache.delete_pattern("*conversacion*")