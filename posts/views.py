from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse
from functools import wraps
from .models import Post, Follow, Comentario

def api_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verifica si la peticion acepta JSON
        accept_header = request.META.get('HTTP_ACCEPT', '')
        if 'application/json' not in accept_header:
            return JsonResponse(
                {'error': 'Esta URL solo acepta peticiones API con Accept: application/json'},
                status=406
            )
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def feed(request):
    # Obtener los usuarios que sigo
    siguiendo = Follow.objects.filter(seguidor=request.user).values_list('seguido', flat=True)
    # Mostrar posts de esos usuarios y los míos
    posts = Post.objects.filter(autor__in=siguiendo) | Post.objects.filter(autor=request.user)
    posts = posts.order_by('-fecha')
    
    # Agregar si puede editar a cada post
    for post in posts:
        post.puede_editar_ahora = post.puede_editar()
        
    return render(request, 'posts/feed.html', {'posts': posts})

@login_required
def crear_post(request):
    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        archivo = request.FILES.get('archivo')
        if contenido:
            Post.objects.create(autor=request.user, contenido=contenido, archivo=archivo)
        return redirect('feed')
    return render(request, 'posts/crear_post.html')

@login_required
def seguir(request, user_id):
    usuario_a_seguir = get_object_or_404(User, id=user_id)
    Follow.objects.get_or_create(seguidor=request.user, seguido=usuario_a_seguir)
    return redirect('feed')

@login_required
def dejar_de_seguir(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    Follow.objects.filter(seguidor=request.user, seguido=usuario).delete()
    return redirect('feed')

@login_required
def editar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, autor=request.user)
    
    if not post.puede_editar():
        return redirect('feed')
    
    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        if contenido:
            post.contenido = contenido
            post.editado = True
            post.fecha_edicion = timezone.now()
            post.save()
        return redirect('feed')
    
    return render(request, 'posts/editar_post.html', {'post': post})

@login_required
def borrar_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, autor=request.user)
    post.delete()
    return redirect('feed')

@login_required
def lista_usuarios(request):
    q = request.GET.get('q', '')
    usuarios = User.objects.exclude(id=request.user.id)
    if q:
        usuarios = usuarios.filter(username__icontains=q)
    siguiendo = Follow.objects.filter(seguidor=request.user).values_list('seguido', flat=True)
    for usuario in usuarios:
        usuario.ya_sigo = usuario.id in siguiendo
        usuario.cant_seguidores = Follow.objects.filter(seguido=usuario).count()
    return render(request, 'posts/usuarios.html', {'usuarios': usuarios, 'q': q})

@login_required
def hashtags(request):
    temas = ['musica', 'comida', 'ropa', 'deporte', 'anime', 'peliculas', 'series', 'lectura', 'estudio', 'trabajo']
    return render(request, 'posts/hashtags.html', {'temas': temas})

@login_required
def hashtag_detalle(request, tema):
    posts = Post.objects.filter(contenido__icontains=f'#{tema}').order_by('-fecha')
    return render(request, 'posts/hashtag_detalle.html', {'tema': tema, 'posts': posts})

@login_required
def menciones(request):
    return render(request, 'posts/menciones.html')

@api_required  # Decorador para forzar JSON
@login_required
def api_feed(request):
    #Verificar si la peticion espera JSON
    accept_header = request.META.get('HTTP_ACCEPT', '')
    if 'application/json' not in accept_header and 'text/html' in accept_header:
        # Si es una peticion normal del navegador, redirigir al feed HTML
        return redirect('feed')
    
    if request.method == 'GET':
        siguiendo = Follow.objects.filter(seguidor=request.user).values_list('seguido', flat=True)
        posts = Post.objects.filter(autor__in=siguiendo) | Post.objects.filter(autor=request.user)
        posts = posts.order_by('-fecha')
        
        data = []
        for post in posts:
            data.append({
                'id': post.id,
                'autor': post.autor.username or post.autor.email or 'desconocido',
                'contenido': post.contenido,
                'fecha': post.fecha.strftime('%d/%m/%Y %H:%M'),
                'editado': post.editado,
            })
        return JsonResponse({'posts': data})

    elif request.method == 'POST':
        import json
        try:
            body = json.loads(request.body)
            contenido = body.get('contenido', '')
            if contenido:
                post = Post.objects.create(autor=request.user, contenido=contenido)
                return JsonResponse({'ok': True, 'id': post.id}, status=201)
            return JsonResponse({'ok': False, 'error': 'contenido vacio'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'JSON invalido'}, status=400)
    
    return JsonResponse({'error': 'Metodo no permitido'}, status=405)
        
@login_required
def api_session_info(request):
    #Verificar autenticacion antes de devolver datos
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    return JsonResponse({
        'usuario': request.user.username or request.user.email,
        'session_key': request.session.session_key,
        'esta_autenticado': request.user.is_authenticated,
        'metodo_http': request.method,
        'cookies': list(request.COOKIES.keys()),
    })

#Endpoint para verificar posts nuevos (polling)
@login_required
def api_nuevos_posts(request):

    ultimo_id = request.GET.get('ultimo_id', 0)
    try:
        ultimo_id = int(ultimo_id)
    except ValueError:
        ultimo_id = 0
    
    siguiendo = Follow.objects.filter(seguidor=request.user).values_list('seguido', flat=True)
    nuevos = Post.objects.filter(
        autor__in=siguiendo
    ).filter(id__gt=ultimo_id).order_by('id')
    
    data = []
    for post in nuevos:
        data.append({
            'id': post.id,
            'autor': post.autor.username,
            'contenido': post.contenido,
            'fecha': post.fecha.strftime('%H:%M'),
            'editado': post.editado,
        })
    
    return JsonResponse({
        'nuevos': data,
        'hay_nuevos': bool(data),
        'ultimo_id': max([p.id for p in nuevos]) if nuevos else ultimo_id
    })

#hastasg API endpoints

@login_required
def api_hashtags(request):
    """
    Devuelve la lista de hashtags con conteo de posts en JSON
    """
    temas = ['musica', 'comida', 'ropa', 'deporte', 'anime', 'peliculas', 
             'series', 'lectura', 'estudio', 'trabajo']
    
    # Contar cuantos posts tiene cada hashtag
    hashtags_data = []
    for tema in temas:
        count = Post.objects.filter(contenido__icontains=f'#{tema}').count()
        hashtags_data.append({
            'nombre': tema,
            'cantidad': count
        })
    
    return JsonResponse({'hashtags': hashtags_data}, status=200)


@login_required
def api_hashtag_detalle(request, tema):
    """
    Devuelve los posts de un hashtag especifico en JSON
    """
    posts = Post.objects.filter(contenido__icontains=f'#{tema}').order_by('-fecha')
    
    data = []
    for post in posts:
        # Determinar tipo de archivo
        archivo_url = None
        es_video = False
        es_audio = False
        es_imagen = False
        
        if post.archivo:
            archivo_url = post.archivo.url
            nombre = post.archivo.name.lower()
            if nombre.endswith('.mp4') or nombre.endswith('.webm') or nombre.endswith('.ogg'):
                es_video = True
            elif nombre.endswith('.mp3') or nombre.endswith('.wav'):
                es_audio = True
            else:
                es_imagen = True
        
        data.append({
            'id': post.id,
            'autor': post.autor.username,
            'contenido': post.contenido,
            'fecha': post.fecha.strftime('%d/%m/%Y %H:%M'),
            'editado': post.editado,
            'archivo': archivo_url,
            'es_video': es_video,
            'es_audio': es_audio,
            'es_imagen': es_imagen,
        })
    
    return JsonResponse({
        'tema': tema,
        'posts': data,
        'total': len(data)
    }, status=200)

# sistema de likes

@login_required
def like_toggle(request, post_id):
    """Versión HTML para redirección"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    
    return redirect('feed')

@login_required
@api_required
def api_like_toggle(request, post_id):
    """Alternar like en un post (API)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    post = get_object_or_404(Post, id=post_id)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        action = 'unliked'
    else:
        post.likes.add(request.user)
        action = 'liked'
    
    return JsonResponse({
        'action': action,
        'likes_count': post.likes.count(),
        'post_id': post.id
    })

# sistema de comentarios

@login_required
def comentar_post(request, post_id):
    """Versión HTML para comentar"""
    if request.method != 'POST':
        return redirect('feed')
    
    post = get_object_or_404(Post, id=post_id)
    contenido = request.POST.get('contenido', '').strip()
    
    if contenido:
        Comentario.objects.create(
            post=post,
            autor=request.user,
            contenido=contenido
        )
    
    return redirect('feed')

@login_required
@api_required
def api_comentarios(request, post_id):
    """Obtener y crear comentarios de un post (API)"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'GET':
        comentarios = post.comentarios.select_related('autor').order_by('fecha')
        
        data = []
        for c in comentarios:
            data.append({
                'id': c.id,
                'autor': c.autor.username,
                'autor_id': c.autor.id,
                'contenido': c.contenido,
                'fecha': c.fecha.strftime('%d/%m/%Y %H:%M'),
                'editado': c.editado,
                'puede_editar': c.autor == request.user
            })
        
        return JsonResponse({'comentarios': data})
    
    elif request.method == 'POST':
        import json
        try:
            body = json.loads(request.body)
            contenido = body.get('contenido', '').strip()
            
            if not contenido:
                return JsonResponse({'error': 'Contenido vacío'}, status=400)
            
            comentario = Comentario.objects.create(
                post=post,
                autor=request.user,
                contenido=contenido
            )
            
            return JsonResponse({
                'id': comentario.id,
                'autor': comentario.autor.username,
                'contenido': comentario.contenido,
                'fecha': comentario.fecha.strftime('%d/%m/%Y %H:%M')
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# notificaciones

@login_required
def notificaciones(request):
    """Vista de notificaciones"""
    return render(request, 'posts/notificaciones.html')

@login_required
@api_required
def api_notificaciones(request):
    """Obtener notificaciones del usuario (API)"""
    # Por ahora solo devolvemos notificaciones de prueba
    # En producción, esto vendría de un modelo de Notificaciones
    return JsonResponse({
        'notificaciones': [
            {
                'id': 1,
                'mensaje': 'Bienvenido a la red social',
                'leido': False,
                'fecha': '2024-01-01T00:00:00'
            }
        ]
    })