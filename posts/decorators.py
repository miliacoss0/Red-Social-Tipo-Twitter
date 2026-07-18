from django.core.cache import cache
from functools import wraps
from django.conf import settings
import hashlib

def cache_page_timeout(timeout=300):  # 5 minutos por defecto
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
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
            
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response
            
            response = view_func(request, *args, **kwargs)
            
            if response.status_code == 200:
                cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator

def invalidar_cache_usuario(usuario_id):
    """Invalidar todas las entradas de caché relacionadas con un usuario"""
    from django.core.cache import cache
    
    # Limpiar caché del feed algorítmico
    cache.delete(f'feed_algoritmico_{usuario_id}')
    
    # Limpiar caché del feed normal
    cache.delete(f'feed_user_{usuario_id}_page_1')
    
    # Limpiar caché de mensajes
    cache.delete_pattern("*mensajes*")
    cache.delete_pattern("*conversacion*")