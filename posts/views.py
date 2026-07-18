from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse
from functools import wraps
from .models import Post, Follow, Comentario, MentionPost
from .utils import extract_mentions, get_mentioned_users, highlight_mentions, api_required
from django.core.cache import cache
from .decorators import cache_page_timeout, invalidar_cache_usuario


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

# posts/views.py - función feed
@login_required
def feed(request):
    siguiendo_ids = Follow.objects.filter(seguidor=request.user).values_list('seguido', flat=True)
    
    autores_ids = list(siguiendo_ids) + [request.user.id]
    
    posts = Post.objects.filter(
        autor__in=autores_ids
    ).select_related('autor').order_by('-fecha')
    
    for post in posts:
        post.puede_editar_ahora = post.puede_editar()
        post.contenido_resaltado = highlight_mentions(post.contenido)
        
    return render(request, 'posts/feed.html', {'posts': posts})

@login_required
def crear_post(request):
    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        archivo = request.FILES.get('archivo')
        if contenido:
            post = Post.objects.create(autor=request.user, contenido=contenido, archivo=archivo)
            
            #procesar menciones
            mencionados = get_mentioned_users(contenido)
            for usuario in mencionados:
                if usuario != request.user:
                    MentionPost.objects.create(
                        post=post,
                        mentioned_user=usuario,
                        mentioned_by=request.user
                    )
            
            #invalidar caché cuando se crea un nuevo post
            invalidar_cache_usuario(request.user.id)
            
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
@cache_page_timeout(60 * 10)  # 10min de caché
def api_feed(request):
    """
    API del feed con optimización y caché.
    """
    accept_header = request.META.get('HTTP_ACCEPT', '')
    if 'application/json' not in accept_header and 'text/html' in accept_header:
        return redirect('feed')
    
    if request.method == 'GET':
        siguiendo = Follow.objects.filter(seguidor=request.user).values_list('seguido', flat=True)
        
        #optimizacion con select_related para el autor
        posts = Post.objects.filter(
            autor__in=siguiendo
        ).select_related('autor').order_by('-fecha')
        
        data = []
        for post in posts:
            data.append({
                'id': post.id,
                'autor': post.autor.username or post.autor.email or 'desconocido',
                'es_mio': post.autor == request.user,
                'puede_editar': post.puede_editar(),
                'contenido': post.contenido,
                'fecha': post.fecha.strftime('%d/%m/%Y %H:%M'),
                'editado': post.editado,
                'archivo_url': post.archivo.url if post.archivo else None,
                'archivo_nombre': post.archivo.name if post.archivo else None,
            })
        return JsonResponse({'posts': data})
    
    elif request.method == 'POST':
        import json
        try:
            body = json.loads(request.body)
            contenido = body.get('contenido', '')
            if contenido:
                post = Post.objects.create(autor=request.user, contenido=contenido)
                #invalidar caché
                invalidar_cache_usuario(request.user.id)
                return JsonResponse({'ok': True, 'id': post.id}, status=201)
            return JsonResponse({'ok': False, 'error': 'contenido vacio'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'JSON invalido'}, status=400)
    
    return JsonResponse({'error': 'Metodo no permitido'}, status=405)
        
@login_required
def api_session_info(request):
    #verificar autenticacion antes de devolver datos
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
@cache_page_timeout(60 * 15)  # 15min de caché
def api_hashtags(request):
    """
    Devuelve la lista de hashtags con conteo de posts en JSON
    """
    temas = ['musica', 'comida', 'ropa', 'deporte', 'anime', 'peliculas', 
             'series', 'lectura', 'estudio', 'trabajo']
    
    hashtags_data = []
    for tema in temas:
        count = Post.objects.filter(contenido__icontains=f'#{tema}').count()
        hashtags_data.append({
            'nombre': tema,
            'cantidad': count
        })
    
    return JsonResponse({'hashtags': hashtags_data}, status=200)


@login_required
@cache_page_timeout(60 * 5)  # 5min de caché
def api_hashtag_detalle(request, tema):
    #optimizacion con select_related para el autor
    posts = Post.objects.filter(
        contenido__icontains=f'#{tema}'
    ).select_related('autor').order_by('-fecha')
    
    data = []
    for post in posts:
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
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido. Usa POST.'
        }, status=405)
    
    post = get_object_or_404(Post, id=post_id)
    usuario = request.user
    
    # ver si el user dio like
    if usuario in post.likes.all():
        post.likes.remove(usuario)
        action = 'unliked'
        mensaje = 'Like eliminado'
    else:
        post.likes.add(usuario)
        action = 'liked'
        mensaje = 'Like agregado'
    
    #obetener últimos 5 usuarios que dieron like 
    ultimos_likes = post.likes.all().order_by('-id')[:5]
    usuarios_likes = [{'id': u.id, 'username': u.username} for u in ultimos_likes]
    
    return JsonResponse({
        'success': True,
        'action': action,
        'mensaje': mensaje,
        'likes_count': post.likes.count(),
        'post_id': post.id,
        'usuario_dio_like': usuario in post.likes.all(),
        'ultimos_likes': usuarios_likes,
        'total_usuarios': post.likes.count()
    }, status=200)
    
@login_required
def api_obtener_likes(request, post_id):
    if request.method != 'GET':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido. Usa GET.'
        }, status=405)
    
    post = get_object_or_404(Post, id=post_id)
    
    # mostrar users q dieron like
    usuarios = post.likes.all().values('id', 'username')
    
    return JsonResponse({
        'success': True,
        'post_id': post.id,
        'likes_count': post.likes.count(),
        'usuario_dio_like': request.user in post.likes.all(),
        'usuarios': list(usuarios)
    }, status=200)

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
# @api_required
def api_comentarios(request, post_id):
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
                'fecha_iso': c.fecha.isoformat(),
                'editado': c.editado,
                'fecha_edicion': c.fecha_edicion.strftime('%d/%m/%Y %H:%M') if c.fecha_edicion else None,
                'puede_editar': c.autor == request.user,
                'es_mio': c.autor == request.user
            })
        
        return JsonResponse({
            'success': True,
            'post_id': post.id,
            'total': len(data),
            'comentarios': data
        }, status=200)
    
    elif request.method == 'POST':
        import json
        try:
            body = json.loads(request.body)
            contenido = body.get('contenido', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
        
        if not contenido:
            return JsonResponse({
                'success': False,
                'error': 'El comentario no puede estar vacío'
            }, status=400)
        
        comentario = Comentario.objects.create(
            post=post,
            autor=request.user,
            contenido=contenido
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Comentario agregado',
            'comentario': {
                'id': comentario.id,
                'autor': comentario.autor.username,
                'autor_id': comentario.autor.id,
                'contenido': comentario.contenido,
                'fecha': comentario.fecha.strftime('%d/%m/%Y %H:%M'),
                'fecha_iso': comentario.fecha.isoformat(),
                'editado': comentario.editado,
                'es_mio': True
            }
        }, status=201)
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    }, status=405)

@login_required
def api_editar_comentario(request, comentario_id):
        # edtiar comentario
    if request.method != 'PUT':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido. Usa PUT.'
        }, status=405)
    
    comentario = get_object_or_404(Comentario, id=comentario_id, autor=request.user)
    
    import json
    try:
        body = json.loads(request.body)
        contenido = body.get('contenido', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    
    if not contenido:
        return JsonResponse({
            'success': False,
            'error': 'El comentario no puede estar vacío'
        }, status=400)
    
    comentario.contenido = contenido
    comentario.editado = True
    comentario.fecha_edicion = timezone.now()
    comentario.save()
    
    return JsonResponse({
        'success': True,
        'mensaje': 'Comentario editado',
        'comentario': {
            'id': comentario.id,
            'contenido': comentario.contenido,
            'editado': comentario.editado,
            'fecha_edicion': comentario.fecha_edicion.strftime('%d/%m/%Y %H:%M')
        }
    }, status=200)
    
@login_required
def api_eliminar_comentario(request, comentario_id):
    """ eliminar comentario"""
    if request.method != 'DELETE':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido. Usa DELETE.'
        }, status=405)
    
    comentario = get_object_or_404(Comentario, id=comentario_id, autor=request.user)
    post_id = comentario.post.id
    comentario.delete()
    
    return JsonResponse({
        'success': True,
        'mensaje': 'Comentario eliminado',
        'comentario_id': comentario_id,
        'post_id': post_id
    }, status=200)
    
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

#Funciones Api para menciones en posts@login_required
@api_required
def api_mis_menciones_posts(request):
    """
    API para obtener menciones en POSTS del usuario autenticado
    """
    menciones = MentionPost.objects.filter(
        mentioned_user=request.user
    ).select_related('post', 'mentioned_by', 'post__autor').order_by('-created_at')
    
    data = []
    for mencion in menciones:
        data.append({
            'id': mencion.id,
            'post_id': mencion.post.id,
            'post_content': mencion.post.contenido,
            'post_autor': mencion.post.autor.username,
            'mentioned_by': mencion.mentioned_by.username,
            'created_at': mencion.created_at.strftime('%d/%m/%Y %H:%M'),
            'is_read': mencion.is_read,
            'tipo': 'post'
        })
    
    return JsonResponse({
        'success': True,
        'menciones': data,
        'total': len(data)
    }, status=200)


@login_required
@api_required
def api_marcar_menciom_post_leida(request, mencion_id):
    """
    Marcar una mención en POST como leída
    """
    mencion = get_object_or_404(MentionPost, id=mencion_id, mentioned_user=request.user)
    mencion.is_read = True
    mencion.save()
    
    return JsonResponse({
        'success': True,
        'mensaje': 'Mención marcada como leída'
    })


@login_required
@api_required
def api_contador_menciones(request):
    """
    Devuelve el conteo de menciones no leídas (posts + tweets)
    """
    from tweets.models import Mention  # Importar desde tweets
    
    posts_no_leidas = MentionPost.objects.filter(
        mentioned_user=request.user,
        is_read=False
    ).count()
    
    tweets_no_leidas = Mention.objects.filter(
        mentioned_user=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({
        'success': True,
        'posts': posts_no_leidas,
        'tweets': tweets_no_leidas,
        'total': posts_no_leidas + tweets_no_leidas
    })
#Vista combinada de menciones (posts + tweets)

@login_required
def todas_menciones(request):
    """
    Vista que combina menciones de POSTS y TWEETS
    """
    from tweets.models import Mention  # Importar desde tweets
    
    # Menciones en posts
    menciones_posts = MentionPost.objects.filter(
        mentioned_user=request.user
    ).select_related('post', 'mentioned_by', 'post__autor')
    
    # Menciones en tweets
    menciones_tweets = Mention.objects.filter(
        mentioned_user=request.user
    ).select_related('tweet', 'mentioned_by')
    
    # Combinar
    todas = []
    
    for m in menciones_posts:
        todas.append({
            'id': m.id,
            'tipo': 'post',
            'contenido': m.post.contenido,
            'autor': m.mentioned_by.username,
            'fecha': m.created_at,
            'url': f'/posts/feed/#post-{m.post.id}',
            'leido': m.is_read,
            'objeto': m
        })
    
    for m in menciones_tweets:
        todas.append({
            'id': m.id,
            'tipo': 'tweet',
            'contenido': m.tweet.content,
            'autor': m.mentioned_by.username,
            'fecha': m.created_at,
            'url': f'/tweets/tweet/{m.tweet.id}/',
            'leido': m.is_read,
            'objeto': m
        })
    
    # Ordenar por fecha (más reciente primero)
    todas.sort(key=lambda x: x['fecha'], reverse=True)
    
    return render(request, 'posts/menciones.html', {
        'menciones': todas
    })

@login_required
def api_borrar_post(request, post_id):
    if request.method == 'DELETE':
        post = get_object_or_404(Post, id=post_id, autor=request.user)
        post.delete()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=405)

@login_required
def api_seguir(request, user_id):
    if request.method == 'POST':
        usuario_a_seguir = get_object_or_404(User, id=user_id)
        Follow.objects.get_or_create(seguidor=request.user, seguido=usuario_a_seguir)
        return JsonResponse({'ok': True, 'siguiendo': True})
    return JsonResponse({'ok': False}, status=405)

@login_required
def api_dejar_de_seguir(request, user_id):
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id)
        Follow.objects.filter(seguidor=request.user, seguido=usuario).delete()
        return JsonResponse({'ok': True, 'siguiendo': False})
    return JsonResponse({'ok': False}, status=405)

@login_required
def api_editar_post(request, post_id):
    if request.method == 'PUT' or request.method == 'POST':
        import json
        post = get_object_or_404(Post, id=post_id, autor=request.user)
        
        if not post.puede_editar():
            return JsonResponse({'ok': False, 'error': 'No se puede editar'}, status=403)
        
        try:
            body = json.loads(request.body)
            contenido = body.get('contenido', '')
            
            if contenido:
                post.contenido = contenido
                post.editado = True
                post.fecha_edicion = timezone.now()
                post.save()
                return JsonResponse({
                    'ok': True,
                    'post': {
                        'id': post.id,
                        'contenido': post.contenido,
                        'editado': post.editado,
                        'fecha_edicion': post.fecha_edicion.strftime('%d/%m/%Y %H:%M')
                    }
                })
            return JsonResponse({'ok': False, 'error': 'Contenido vacío'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)
    return JsonResponse({'ok': False}, status=405)

@login_required
def api_usuarios(request):
    if request.method == 'GET':
        q = request.GET.get('q', '')
        usuarios = User.objects.exclude(id=request.user.id)
        if q:
            usuarios = usuarios.filter(username__icontains=q)
        
        siguiendo = Follow.objects.filter(seguidor=request.user).values_list('seguido', flat=True)
        
        data = []
        for usuario in usuarios[:20]:
            data.append({
                'id': usuario.id,
                'username': usuario.username,
                'ya_sigo': usuario.id in siguiendo,
                'cant_seguidores': Follow.objects.filter(seguido=usuario).count(),
            })
        return JsonResponse({'usuarios': data})
    return JsonResponse({'ok': False}, status=405)

@login_required
def api_menciones(request):
    """Obtener menciones del usuario."""
    if request.method == 'GET':
        username = request.user.username
        #optimizacion con select_related para el autor
        posts = Post.objects.filter(
            contenido__icontains=f'@{username}'
        ).select_related('autor').order_by('-fecha')
        
        data = []
        for post in posts[:20]:
            data.append({
                'id': post.id,
                'autor': post.autor.username,
                'contenido': post.contenido,
                'fecha': post.fecha.strftime('%d/%m/%Y %H:%M'),
            })
        return JsonResponse({'menciones': data})
    return JsonResponse({'ok': False}, status=405)
