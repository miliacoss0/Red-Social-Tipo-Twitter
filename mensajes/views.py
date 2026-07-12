from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db.models import Q
from django.core.cache import cache
from .models import Conversacion, Mensaje
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

User = get_user_model()

@login_required
def inbox(request):
    """Bandeja de entrada"""
    conversaciones = Conversacion.objects.filter(
        participantes=request.user
    ).prefetch_related('participantes').order_by('-actualizado')
    
    # Agregar información del otro usuario
    for conv in conversaciones:
        conv.otro_usuario = conv.participantes.exclude(id=request.user.id).first()
        conv.ultimo_mensaje = conv.mensajes.order_by('-fecha_envio').first()
        conv.mensajes_no_leidos = conv.mensajes.filter(
            leido=False
        ).exclude(emisor=request.user).count()
    
    return render(request, 'mensajes/inbox.html', {
        'conversaciones': conversaciones
    })

@login_required
def conversacion(request, user_id):
    """Ver conversación con un usuario"""
    otro_usuario = get_object_or_404(User, id=user_id)
    
    # Obtener o crear conversación
    conversacion = Conversacion.objects.filter(
        participantes=request.user
    ).filter(participantes=otro_usuario).first()
    
    if not conversacion:
        conversacion = Conversacion.objects.create()
        conversacion.participantes.add(request.user, otro_usuario)
    
    # Marcar mensajes como leídos
    Mensaje.objects.filter(
        conversacion=conversacion,
        emisor=otro_usuario,
        leido=False
    ).update(leido=True)
    
    # Obtener mensajes con optimización
    mensajes = conversacion.mensajes.select_related('emisor').order_by('fecha_envio')
    
    return render(request, 'mensajes/conversacion.html', {
        'conversacion': conversacion,
        'otro_usuario': otro_usuario,
        'mensajes': mensajes
    })

@login_required
def api_enviar_mensaje(request):
    """Enviar mensaje (API)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        receptor_id = data.get('receptor_id')
        contenido = data.get('contenido', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    
    if not contenido:
        return JsonResponse({'error': 'Mensaje vacío'}, status=400)
    
    receptor = get_object_or_404(User, id=receptor_id)
    
    # Obtener o crear conversación
    conversacion = Conversacion.objects.filter(
        participantes=request.user
    ).filter(participantes=receptor).first()
    
    if not conversacion:
        conversacion = Conversacion.objects.create()
        conversacion.participantes.add(request.user, receptor)
    
    mensaje = Mensaje.objects.create(
        conversacion=conversacion,
        emisor=request.user,
        contenido=contenido
    )
    
    # Actualizar timestamp de conversación
    conversacion.save()
    
    # Invalidar cache
    try:
        cache.delete(f'chat_{conversacion.id}')
    except Exception:
        pass
    
    return JsonResponse({
        'status': 'enviado',
        'mensaje_id': mensaje.id,
        'fecha': mensaje.fecha_envio.isoformat(),
        'emisor': request.user.username,
        'contenido': mensaje.contenido
    })

@login_required
def api_obtener_mensajes(request, conversacion_id):
    """Obtener mensajes de una conversación (API)"""
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)
    
    if not conversacion.participantes.filter(id=request.user.id).exists():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    # Intentar cache
    cache_key = f'chat_{conversacion_id}_{request.user.id}'
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        return JsonResponse(cached_data)
    
    mensajes = conversacion.mensajes.select_related('emisor').order_by('fecha_envio')
    
    data = []
    for msg in mensajes:
        data.append({
            'id': msg.id,
            'emisor': msg.emisor.username,
            'emisor_id': msg.emisor.id,
            'contenido': msg.contenido,
            'fecha': msg.fecha_envio.isoformat(),
            'es_mio': msg.emisor == request.user,
            'leido': msg.leido
        })
    
    result = {'mensajes': data}
    cache.set(cache_key, result, 60)  # Cache por 1 minuto
    
    return JsonResponse(result)

@login_required
def api_marcar_leido(request, mensaje_id):
    """Marcar mensaje como leído (API)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    mensaje = get_object_or_404(Mensaje, id=mensaje_id)
    
    if mensaje.emisor == request.user:
        return JsonResponse({'error': 'No puedes marcar tus propios mensajes'}, status=403)
    
    if not mensaje.conversacion.participantes.filter(id=request.user.id).exists():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    mensaje.marcar_como_leido()
    
    return JsonResponse({'status': 'ok'})

@login_required
def api_conversaciones(request):
    conversaciones = Conversacion.objects.filter(
        participantes=request.user
    ).prefetch_related('participantes')

    data = []

    for c in conversaciones:
        otro = c.participantes.exclude(id=request.user.id).first()
        ultimo = c.mensajes.order_by('-fecha_envio').first()

        data.append({
            'id': c.id,
            'usuario': otro.username if otro else None,
            'ultimo_mensaje': ultimo.contenido if ultimo else '',
            'actualizado': c.actualizado.isoformat(),
        })

    return JsonResponse({'conversaciones': data})