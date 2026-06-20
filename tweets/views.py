from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q  # Para búsquedas complejas
from .models import Tweet, HashTag
from .forms import TweetForm
from .models import Mention # Debe importar Mention


def home(request):
    """
    Vista principal: muestra el timeline con todos los tweets.
    """
    # Obtener todos los tweets (los más recientes primero)
    tweets = Tweet.objects.all()
    
    # Formulario para crear nuevo tweet (solo si el usuario está logueado)
    if request.method == 'POST' and request.user.is_authenticated:
        form = TweetForm(request.POST)
        if form.is_valid():
            tweet = form.save(commit=False)  # No guardar aún
            tweet.author = request.user      # Asignar el autor
            tweet.save()                     # Guardar (activa el procesamiento de hashtags)
            return redirect('feed_home')
    else:
        form = TweetForm()
    
    
    # Procesar cada tweet para resaltar menciones 
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


# -----------
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