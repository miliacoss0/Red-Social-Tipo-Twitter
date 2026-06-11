from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post, Follow
from django.utils import timezone

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
    usuarios = User.objects.exclude(id=request.user.id)  # todos menos yo
    siguiendo = Follow.objects.filter(seguidor=request.user).values_list('seguido', flat=True)
    
    for usuario in usuarios:
        usuario.ya_sigo = usuario.id in siguiendo
        usuario.cant_seguidores = Follow.objects.filter(seguido=usuario).count()
    
    return render(request, 'posts/usuarios.html', {'usuarios': usuarios})