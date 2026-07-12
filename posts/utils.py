# posts/utils.py

import re
from django.http import JsonResponse
from functools import wraps
from django.contrib.auth.models import User
from django.shortcuts import redirect

def api_required(view_func):
    """
    Decorador para forzar que una vista solo acepte peticiones API.
    Verifica que el header Accept contenga application/json.
    Si no, redirige a feed en lugar de dar error 406.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        accept_header = request.META.get('HTTP_ACCEPT', '')
        if 'application/json' not in accept_header:
            return redirect('feed')
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
#Funciones para menciones

def extract_mentions(text):
    """
    Extrae todos los nombres de usuario mencionados en un texto
    Formato: @usuario
    """
    pattern = r'@([\w\-]+)'
    mentions = re.findall(pattern, text)
    return list(set(mentions))  # Eliminar duplicados

def get_mentioned_users(text):
    """
    Obtiene los objetos User de las menciones en un texto
    """
    usernames = extract_mentions(text)
    users = []
    for username in usernames:
        try:
            user = User.objects.get(username=username)
            users.append(user)
        except User.DoesNotExist:
            pass  # Usuario no existe, ignorar
    return users

def highlight_mentions(text):
    """
    Convierte @usuario en un enlace clickeable
    """
    def replace_mention(match):
        username = match.group(1)
        return f'<a href="/tweets/perfil/{username}/" class="mention-link">@{username}</a>'
    
    highlighted = re.sub(r'@([\w\-]+)', replace_mention, text)
    return highlighted