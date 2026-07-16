from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db.models import Q
from django.core.cache import cache
from django.views.decorators.http import require_http_methods
from .models import Conversacion, Mensaje
import json
from django.db.models import Q
from posts.decorators import cache_page_timeout

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
@cache_page_timeout(60 * 2)  # 2min de caché
def conversacion(request, usuario_id):
    """Vista de conversación con optimización de queries."""
    otro_usuario = get_object_or_404(User, id=usuario_id)
    
    #optimizacion con select_related para emisor y receptor
    mensajes = Mensaje.objects.filter(
        (Q(emisor=request.user, receptor=otro_usuario) |
         Q(emisor=otro_usuario, receptor=request.user))
    ).select_related('emisor', 'receptor').order_by('fecha_envio')
    
    return render(request, 'mensajes/conversacion.html', {
        'mensajes': mensajes,
        'otro_usuario': otro_usuario
    })

@login_required
@require_http_methods(["POST"])
def api_enviar_mensaje(request):
    """Enviar mensaje (API)"""
    try:
        data = json.loads(request.body)
        receptor_id = data.get('receptor_id')
        contenido = data.get('contenido', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    
    if not contenido:
        return JsonResponse({'success': False,'error': 'El mensaje no puede estar vacío'}, status=400)
    
    if not receptor_id:
        return JsonResponse({'success': False,'error': 'ID del receptor no proporcionado'}, status=400)
    
    try:
        receptor = get_object_or_404(User, id=receptor_id)
    except User.DoesNotExist:
        return JsonResponse({'success': False,'error': 'Usuario receptor no encontrado'}, status=404)
    
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
    
    # Incluir información del mensaje en la respuesta
    return JsonResponse({
        'success': True,
        'mensaje': {
            'id': mensaje.id,
            'emisor': request.user.username,
            'emisor_id': request.user.id,
            'contenido': mensaje.contenido,
            'fecha': mensaje.fecha_envio.isoformat(),
            'es_mio': True,
            'leido': mensaje.leido
        }
    })

@login_required
def api_obtener_mensajes(request, conversacion_id):
    """Obtener mensajes de una conversación (API)"""
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)
    
    if not conversacion.participantes.filter(id=request.user.id).exists():
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
    
    # Obtener el otro usuario de la conversación
    otro_usuario = conversacion.participantes.exclude(id=request.user.id).first()
    
    # Marcar mensajes del otro usuario como leídos
    if otro_usuario:
        Mensaje.objects.filter(
            conversacion=conversacion,
            emisor=otro_usuario,
            leido=False
        ).update(leido=True)
    
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
    
    return JsonResponse({
        'success': True,
        'mensajes': data
    })

@login_required
@require_http_methods(["POST"])
def api_marcar_leido(request, mensaje_id):
    """Marcar mensaje como leído (API) con respuesta JSON"""
    mensaje = get_object_or_404(Mensaje, id=mensaje_id)
    
    if mensaje.emisor == request.user:
        return JsonResponse({
            'success': False,
            'error': 'No puedes marcar tus propios mensajes'
        }, status=403)
    
    if not mensaje.conversacion.participantes.filter(id=request.user.id).exists():
        return JsonResponse({
            'success': False,
            'error': 'No autorizado'
        }, status=403)
    
    mensaje.marcar_como_leido()
    
    return JsonResponse({
        'success': True,
        'mensaje_id': mensaje_id,
        'leido': True
    })

@login_required
def api_conversaciones(request):
    """Obtener lista de conversaciones (API)"""
    conversaciones = Conversacion.objects.filter(
        participantes=request.user
    ).prefetch_related('participantes').order_by('-actualizado')
    
    data = []
    for c in conversaciones:
        otro = c.participantes.exclude(id=request.user.id).first()
        ultimo = c.mensajes.order_by('-fecha_envio').first()
        no_leidos = c.mensajes.filter(
            leido=False
        ).exclude(emisor=request.user).count()
        
        if otro:
            # OBTENER LA URL DEL AVATAR DE GITHUB
            avatar_url = None
            try:
                social = otro.socialaccount_set.first()
                if social:
                    if social.provider == 'github':
                        avatar_url = social.extra_data.get('avatar_url')
                    else:
                        avatar_url = social.get_avatar_url()
            except:
                pass
            
            # Si no hay avatar, usar ui-avatars como fallback
            if not avatar_url:
                avatar_url = f"https://ui-avatars.com/api/?name={otro.username}&background=007bff&color=fff&size=50"
            
            data.append({
                'id': c.id,
                'usuario_id': otro.id,
                'usuario_nombre': otro.username,
                'avatar_url': avatar_url,
                'ultimo_mensaje': ultimo.contenido if ultimo else '',
                'fecha_actualizado': c.actualizado.isoformat(),
                'no_leidos': no_leidos,
                'tiene_mensajes': c.mensajes.exists()
            })
    
    return JsonResponse({
        'success': True,
        'conversaciones': data
    })