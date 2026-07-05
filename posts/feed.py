from django.db.models import Q, Count, Case, When, Value, IntegerField, F
from django.core.cache import cache
from datetime import datetime, timedelta
from .models import Post
from .feed import get_feed_for_user

def get_feed_for_user(user, page=1, per_page=20):
    """Obtener feed personalizado con scoring"""
    cache_key = f'feed_user_{user.id}_page_{page}'
    cached = cache.get(cache_key)
    
    if cached is not None:
        return cached
    
    following_ids = user.following.values_list('followed_id', flat=True)
    
    posts = Post.objects.filter(
        Q(autor__in=following_ids) | Q(autor=user)
    ).select_related('autor').prefetch_related('likes', 'hashtags').annotate(
        score=Case(
            When(autor__in=following_ids, then=Value(10)),
            When(likes__isnull=False, then=Value(5)),
            When(fecha_creacion__gte=datetime.now() - timedelta(hours=24), then=Value(3)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('-score', '-fecha_creacion')
    
    start = (page - 1) * per_page
    end = page * per_page
    result = list(posts[start:end])
    
    cache.set(cache_key, result, 300)  # 5 minutos
    return result

def invalidate_feed_cache(user_id):
    """Invalidar cache del feed"""
    from django.core.cache import cache
    # En producción, usaríamos pattern matching
    cache.delete(f'feed_user_{user_id}_page_1')
    # Podrías agregar más páginas