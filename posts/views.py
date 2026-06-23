from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post, Follow
from django.utils import timezone
from django.http import JsonResponse

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

#funciones para que la pagina no recargue

@login_required
def api_feed(request):
    if request.method == 'GET':
        siguiendo = Follow.objects.filter(seguidor=request.user).values_list('seguido', flat=True)
        posts = Post.objects.filter(autor__in=siguiendo) | Post.objects.filter(autor=request.user)
        posts = posts.order_by('-fecha')
        
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
        body = json.loads(request.body)
        contenido = body.get('contenido', '')
        if contenido:
            post = Post.objects.create(autor=request.user, contenido=contenido)
            return JsonResponse({'ok': True, 'id': post.id}, status=201)
        return JsonResponse({'ok': False, 'error': 'contenido vacío'}, status=400)

@login_required
def api_session_info(request):
    # Devuelve información sobre el token de sesión actual
    return JsonResponse({
        'usuario': request.user.username or request.user.email,
        'session_key': request.session.session_key,  # el token de sesión
        'esta_autenticado': request.user.is_authenticated,
        'metodo_http': request.method,  # GET, POST, etc.
        'cookies': list(request.COOKIES.keys()),  # cookies disponibles
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
        usuario_a_seguir = get_object_or_404(User, user_id)
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
def api_hashtags(request):
    if request.method == 'GET':
        temas = ['musica', 'comida', 'ropa', 'deporte', 'anime', 'peliculas', 
                 'series', 'lectura', 'estudio', 'trabajo']
        data = []
        for tema in temas:
            count = Post.objects.filter(contenido__icontains=f'#{tema}').count()
            data.append({
                'tema': tema,
                'cantidad': count
            })
        return JsonResponse({'hashtags': data})
    return JsonResponse({'ok': False}, status=405)

@login_required
def api_hashtag_detalle(request, tema):
    if request.method == 'GET':
        posts = Post.objects.filter(contenido__icontains=f'#{tema}').order_by('-fecha')
        data = []
        for post in posts[:20]:
            data.append({
                'id': post.id,
                'autor': post.autor.username,
                'contenido': post.contenido,
                'fecha': post.fecha.strftime('%d/%m/%Y %H:%M'),
                'es_mio': post.autor == request.user,
            })
        return JsonResponse({
            'tema': tema,
            'posts': data
        })
    return JsonResponse({'ok': False}, status=405)

@login_required
def api_menciones(request):
    if request.method == 'GET':
        username = request.user.username
        posts = Post.objects.filter(contenido__icontains=f'@{username}').order_by('-fecha')
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