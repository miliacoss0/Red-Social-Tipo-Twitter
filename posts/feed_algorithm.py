# posts/feed_algorithm.py

from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Count, Q
from .models import Post, Comentario
from django.contrib.auth.models import User

PESO_TIEMPO = 0.35          
PESO_POPULARIDAD = 0.25     
PESO_AUTOR = 0.20           
PESO_INTERACCION = 0.20    
def calcular_peso_post(post, usuario=None):
    """
    Calcula el peso/relevancia de un post para un usuario específico
    Retorna un valor entre 0 y 1
    """
    peso = 0.0
    
    # 1. FACTOR TIEMPO (35%) - Más nuevo = más peso
    horas_antiguedad = (timezone.now() - post.fecha).total_seconds() / 3600
    factor_tiempo = max(0, 1 - (horas_antiguedad / 48))  # Decae en 48 horas
    peso += factor_tiempo * PESO_TIEMPO
    
    # 2. FACTOR POPULARIDAD (25%) - Likes + Comentarios
    total_interacciones = post.likes.count() + post.comentarios.count()
    factor_popularidad = min(total_interacciones / 30, 1)  # Normalizar a 0-1
    peso += factor_popularidad * PESO_POPULARIDAD
    
    # 3. FACTOR AUTOR (20%) - Seguidores del autor
    seguidores_autor = post.autor.followers.count()
    factor_autor = min(seguidores_autor / 50, 1)
    peso += factor_autor * PESO_AUTOR
    
    # 4. FACTOR INTERACCIÓN (20%) - Si el usuario ha interactuado con el autor
    if usuario:
        interacciones = get_interacciones_usuario(usuario, post.autor)
        factor_interaccion = min(interacciones / 10, 1)
        peso += factor_interaccion * PESO_INTERACCION
    
    return round(peso, 4)

def get_interacciones_usuario(usuario, autor):
    """
    Cuenta interacciones previas del usuario con el autor
    """
    # Likes que el usuario ha dado a posts del autor
    likes_dados = Post.objects.filter(
        autor=autor,
        likes=usuario
    ).count()
    
    # Comentarios que el usuario ha hecho en posts del autor
    comentarios_hechos = Comentario.objects.filter(
        post__autor=autor,
        autor=usuario
    ).count()
    
    return likes_dados + comentarios_hechos

def actualizar_peso_post(post, usuario=None):
    """Actualiza el peso de un post y lo guarda en la BD"""
    post.peso = calcular_peso_post(post, usuario)
    post.save(update_fields=['peso'])
    return post.peso

def actualizar_pesos_masivos():
    """
    Actualiza pesos de todos los posts (para tareas programadas)
    """
    posts = Post.objects.all().select_related('autor')
    total = posts.count()
    
    if total == 0:
        print("No hay posts para actualizar")
        return 0
    
    print(f"Actualizando {total} posts...")
    
    for i, post in enumerate(posts):
        post.peso = calcular_peso_post(post)
        post.save(update_fields=['peso'])
        
        if (i + 1) % 100 == 0 or (i + 1) == total:
            print(f"  Procesados {i + 1}/{total} posts")
    
    print(f"Pesos actualizados para {total} posts")
    return total

def calcular_peso_tweet(tweet, usuario=None):
    """
    Calcula el peso/relevancia de un TWEET
    """
    peso = 0.0
    
    # 1. FACTOR TIEMPO (35%)
    horas_antiguedad = (timezone.now() - tweet.created_at).total_seconds() / 3600
    factor_tiempo = max(0, 1 - (horas_antiguedad / 48))
    peso += factor_tiempo * PESO_TIEMPO
    
    # 2. FACTOR AUTOR (40% para tweets, ya que no tienen likes/comentarios)
    seguidores_autor = tweet.author.followers.count()
    factor_autor = min(seguidores_autor / 50, 1)
    peso += factor_autor * 0.40
    
    # 3. FACTOR INTERACCIÓN (25% para tweets)
    if usuario:
        from .models import Follow
        # Si el usuario sigue al autor, más peso
        if Follow.objects.filter(seguidor=usuario, seguido=tweet.author).exists():
            peso += 0.25
    
    return round(peso, 4)