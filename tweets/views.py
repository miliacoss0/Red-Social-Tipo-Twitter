import re  
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q  # Para búsquedas complejas
from .models import Tweet, HashTag
from .forms import TweetForm
from .models import Mention # Debe importar Mention
from django.db.models import Q
from django.http import JsonResponse 


def home(request):
    if request.user.is_authenticated:
        from follows.models import Follow as FollowNuevo
        from posts.models import Follow as FollowViejo
        
        # IDs de usuarios seguidos en ambos sistemas
        siguiendo_nuevo = FollowNuevo.objects.filter(
            follower=request.user
        ).values_list('followed', flat=True)
        
        siguiendo_viejo = FollowViejo.objects.filter(
            seguidor=request.user
        ).values_list('seguido', flat=True)
        
        # Combinar ambas listas
        todos_siguiendo = list(siguiendo_nuevo) + list(siguiendo_viejo)
        
        tweets = Tweet.objects.filter(
            Q(author__in=todos_siguiendo) | Q(author=request.user)
        ).order_by('-created_at')
    else:
        tweets = Tweet.objects.all().order_by('-created_at')
    if request.method == 'POST' and request.user.is_authenticated:
        form = TweetForm(request.POST)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.author = request.user
            tweet.save()
            return redirect('feed_home')
    else:
        form = TweetForm()
    
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

#Endpoints api para manejar tweets en formato JSON

def api_tweets(request):
    if request.method == 'GET':
        # Obtener todos los tweets ordenados por fecha descendente
        tweets = Tweet.objects.all().order_by('-created_at')
        data = []
        for tweet in tweets:
            data.append({
                'id': tweet.id,
                'author': tweet.author.username,
                'content': tweet.content,
                'created_at': tweet.created_at.strftime('%d/%m/%Y %H:%M'),
                'hashtags': [tag.name for tag in tweet.hashtags.all()],
                'mentions': [user.username for user in tweet.get_mentions()]
            })
        #Devolver respuesta JSON con los tweets
        return JsonResponse({'tweets': data}, status=200)
    
    elif request.method == 'POST':
        #Manejar creacion de tweets via API
        try:
            #Parsear el cuerpo de la peticion como JSON
            body = json.loads(request.body)
            content = body.get('content', '')
            
            #Validar que el contenido no este vacio
            if not content or content.strip() == '':
                return JsonResponse({'error': 'El contenido no puede estar vacio'}, status=400)
            
            #Validar limite de caracteres
            if len(content) > 280:
                return JsonResponse({'error': 'El tweet excede los 280 caracteres'}, status=400)
            
            #Crear el tweet
            tweet = Tweet.objects.create(
                author=request.user,
                content=content.strip()
            )
            
            #Devolver respuesta de exito con el ID del tweet creado
            return JsonResponse({
                'ok': True,
                'id': tweet.id,
                'message': 'Tweet creado exitosamente'
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON invalido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    #Metodo HTTP no permitido
    return JsonResponse({'error': 'Metodo no permitido'}, status=405)


def api_tweets_usuario(request, username):
    #API endpoint que devuelve los tweets de un usuario especifico en JSON.

    from django.contrib.auth.models import User
    
    try:
        #Buscar el usuario por nombre de usuario
        usuario = User.objects.get(username=username)
    except User.DoesNotExist:
        #Usuario no encontrado
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    
    # Obtener tweets del usuario
    tweets = Tweet.objects.filter(author=usuario).order_by('-created_at')
    data = []
    for tweet in tweets:
        data.append({
            'id': tweet.id,
            'author': tweet.author.username,
            'content': tweet.content,
            'created_at': tweet.created_at.strftime('%d/%m/%Y %H:%M'),
            'hashtags': [tag.name for tag in tweet.hashtags.all()]
        })
    
    # Devolver respuesta JSON con los tweets del usuario
    return JsonResponse({
        'usuario': usuario.username,
        'tweets': data,
        'total': len(data)
    }, status=200)


def api_tweets_hashtag(request, tag_name):
    try:
        # Buscar el hashtag
        hashtag = HashTag.objects.get(name=tag_name.lower())
    except HashTag.DoesNotExist:
        # Hashtag no encontrado
        return JsonResponse({'error': 'Hashtag no encontrado'}, status=404)
    
    # Obtener tweets del hashtag
    tweets = hashtag.tweets.all().order_by('-created_at')
    data = []
    for tweet in tweets:
        data.append({
            'id': tweet.id,
            'author': tweet.author.username,
            'content': tweet.content,
            'created_at': tweet.created_at.strftime('%d/%m/%Y %H:%M')
        })
    
    # Devolver respuesta JSON con los tweets del hashtag
    return JsonResponse({
        'hashtag': hashtag.name,
        'tweets': data,
        'total': len(data)
    }, status=200)


def api_mis_menciones(request):
    # Verificar que el usuario este autenticado
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
    
    # Obtener menciones del usuario
    menciones = Mention.objects.filter(
        mentioned_user=request.user
    ).select_related('tweet', 'mentioned_by').order_by('-created_at')
    
    data = []
    for mencion in menciones:
        data.append({
            'id': mencion.id,
            'tweet_id': mencion.tweet.id,
            'tweet_content': mencion.tweet.content,
            'mentioned_by': mencion.mentioned_by.username,
            'created_at': mencion.created_at.strftime('%d/%m/%Y %H:%M'),
            'is_read': mencion.is_read
        })
    
    # Marcar todas las menciones como leidas
    menciones.update(is_read=True)
    
    # Devolver respuesta JSON con las menciones
    return JsonResponse({
        'menciones': data,
        'total': len(data)
    }, status=200)


def api_buscar_tweets(request):
    # Obtener el parametro de busqueda
    query = request.GET.get('q', '')
    
    # Validar que se haya enviado un parametro de busqueda
    if not query:
        return JsonResponse({'error': 'Parametro de busqueda q requerido'}, status=400)
    
    # Realizar la busqueda
    results = Tweet.objects.filter(
        Q(content__icontains=query) |
        Q(author__username__icontains=query) |
        Q(hashtags__name__icontains=query)
    ).distinct().order_by('-created_at')
    
    data = []
    for tweet in results:
        data.append({
            'id': tweet.id,
            'author': tweet.author.username,
            'content': tweet.content,
            'created_at': tweet.created_at.strftime('%d/%m/%Y %H:%M'),
            'hashtags': [tag.name for tag in tweet.hashtags.all()]
        })
    
    # Devolver respuesta JSON con los resultados
    return JsonResponse({
        'query': query,
        'results': data,
        'total': len(data)
    }, status=200)


def api_session_info(request):
    # Verificar que el usuario este autenticado
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    # Devolver informacion de la sesion
    return JsonResponse({
        'usuario': request.user.username,
        'email': request.user.email,
        'esta_autenticado': request.user.is_authenticated,
        'session_key': request.session.session_key,
        'cookies': list(request.COOKIES.keys())
    }, status=200)