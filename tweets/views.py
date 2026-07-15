from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from django.contrib import messages
from django.db.models import Q  # Para búsquedas complejas
from django.db.models import Case, When, Value, IntegerField
from .models import Tweet, HashTag, Mention, Comentario, Follow      #Agregar Follow
from .forms import TweetForm, ComentarioForm   # Formularios


def home(request):
    """
    Feed personalizado algorítmico:
    - Primero: tweets de usuarios que sigues
    - Luego: tweets de usuarios que no sigues
    - Ambos ordenados por fecha (más recientes primero)
    """
    
    if not request.user.is_authenticated:
        # Si no está logueado, mostrar todos los tweets 
        tweets = Tweet.objects.all().order_by('-created_at')
    else:
        #Obtener los IDs de usuarios que sigue
        followed_users = Follow.objects.filter(
            follower=request.user
        ).values_list('followed_id', flat=True)

        #Obtener todos los tweets
        all_tweets = Tweet.objects.all()

        # Anotar con un campo "score" para que se pueda ordenar:
        # El 1 representa "de usuarios que sigues", y el 0 representa "de usuarios que no sigues"
        tweets = all_tweets.annotate(
            is_followed=Case(
                When(author__in=followed_users, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).order_by('-is_followed', '-created_at')
    
    # Formulario para crear tweet
    if request.method == 'POST' and request.user.is_authenticated:
        form = TweetForm(request.POST)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.author = request.user
            tweet.save()
            return redirect('feed_home')
    else:
        form = TweetForm()

    # Procesar las menciones resaltadas
    for tweet in tweets:
        tweet.content_display = highlight_mentions(tweet.content)
    
    context = {
        'tweets': tweets,
        'form': form,
    }
    return render(request, 'tweets/home.html', context)
    


def highlight_mentions(text):
    """
    Convierte @usuario en un enlace clickeable
    """
    import re
    # Buscar patrones @usuario y convertirlos en enlaces
    def replace_mention(match):
        username = match.group(1)
        return f'<a href="/perfil/{username}/" class="mention-link">@{username}</a>'
    
    highlighted = re.sub(r'@(\w+)', replace_mention, text)
    return highlighted


def search(request):
    """
    Buscador de tweets por texto, hashtags o usuarios.
    """
    query = request.GET.get('q', '')  # Obtener el parámetro 'q' de la URL
    results = []
    
    if query:
        # Búsqueda con Q objects (permite múltiples condiciones)
        # icontains = búsqueda sin distinción de mayúsculas/minúsculas
        results = Tweet.objects.filter(
            Q(content__icontains=query) |           # El texto contiene la búsqueda
            Q(author__username__icontains=query) |   # El nombre de usuario contiene la búsqueda
            Q(hashtags__name__icontains=query)       # El hashtag contiene la búsqueda
        ).distinct()  # distinct() evita duplicados
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'tweets/search.html', context)


def hashtag_view(request, tag_name):
    """
    Muestra todos los tweets que tienen un hashtag específico.
    """
    hashtag = get_object_or_404(HashTag, name=tag_name.lower())
    tweets = hashtag.tweets.all()  # Todos los tweets con este hashtag
    
    context = {
        'hashtag': hashtag,
        'tweets': tweets,
    }
    return render(request, 'tweets/hashtag.html', context)


def mis_menciones(request):
    """
    Muestra todos los tweets donde han mencionado al usuario logueado.
    """
    # Obtener todas las menciones del usuario actual
    menciones = Mention.objects.filter(
        mentioned_user=request.user
    ).select_related('tweet', 'mentioned_by')
    
    # Contar las no leídas
    total_no_leidas = menciones.filter(is_read=False).count()
    
    # Marcar como leídas
    menciones.update(is_read=True)
    
    context = {
        'menciones': menciones,  # ← CLAVE: debe llamarse 'menciones'
        'total_no_leidas': total_no_leidas,
    }
    return render(request, 'tweets/menciones.html', context)


def tweet_detalle(request, tweet_id):
    """
    Muestra un tweet específico.
    """
    from .models import Tweet
    tweet = get_object_or_404(Tweet, id=tweet_id)
    return render(request, 'tweets/tweet_detalle.html', {'tweet': tweet})


# Nueva Vista: perfil_usuario (Perfil de usuario)
# -----------
def perfil_usuario(request, username):
    """
    Muestra el perfil de un usuario y sus tweets
    """
    from django.contrib.auth.models import User
    

    usuario = get_object_or_404(User, username=username)
    tweets = Tweet.objects.filter(author=usuario).order_by('-created_at')
    
    context = {
        'perfil_usuario': usuario,
        'tweets': tweets,
    }
    return render(request, 'tweets/perfil_usuario.html', context)

# Nueva Vista: hashtags_populares (Lista de hashtags más usados)
# --------
def hashtags_populares(request):
    """
    Muestra los hashtags más utilizados ordenados por popularidad
    """
    from django.db.models import Count
    
    # Obtener hashtags ordenados por cantidad de tweets (los más populares)
    hashtags = HashTag.objects.annotate(
        total_tweets=Count('tweets')
    ).order_by('-total_tweets')[:20]  # Top 20
    
    context = {
        'hashtags': hashtags,
    }
    return render(request, 'tweets/hashtags_populares.html', context)

# Nueva Vista: comentarios (Página de comentarios)
# ------
def comentarios(request, tweet_id):
    """
    Muestra y procesa comentarios de un tweet específico
    """
    tweet = get_object_or_404(Tweet, id=tweet_id)
    comentarios = Comentario.objects.filter(tweet=tweet)
    
    # Procesar nuevo comentario
    if request.method == 'POST' and request.user.is_authenticated:
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.tweet = tweet
            comentario.author = request.user
            comentario.save()
            messages.success(request, '¡Comentario publicado!')
            return redirect('comentarios', tweet_id=tweet.id)
    else:
        form = ComentarioForm()
    
    context = {
        'tweet': tweet,
        'comentarios': comentarios,
        'form': form,
    }
    return render(request, 'tweets/comentarios.html', context)


@login_required
def follow_user(request, username):
    """
    Vista para que se pueda seguir a un usuario
    """
    user_to_follow = get_object_or_404(User, username=username)

    # No puedes seguirte a ti mismo
    if request.user == user_to_follow:
        messages.error(request, 'No puedes seguirte a ti mismo')
        return redirect('perfil_usuario', username=username)
    
    # Verificar si ya lo sigues 
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        followed=user_to_follow
    )

    if created:
        messages.success(request, f'Ahora estás siguiendo a @{username}')
    else:
        messages.info(request, f'Ya sigues a @{username}')
    
    return redirect('perfil_usuario', username)


@login_required
def unfollow_user(request, username):
    """
    Vista para dejar de seguir a un usuario
    """
    user_to_unfollow = get_object_or_404(User, username=username)

    Follow.objects.filter(
        follower=request.user,
        followed=user_to_unfollow
    ).delete()

    messages.success(request, f'Dejaste de seguir a @{username}')
    return redirect('perfil_usuario', username=username)