from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Follow

User = get_user_model()

@login_required
def toggle_follow(request, user_id):
    """Alternar seguir/dejar de seguir (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    user_to_follow = get_object_or_404(User, id=user_id)
    
    if request.user == user_to_follow:
        return JsonResponse({'error': 'No puedes seguirte a ti mismo'}, status=400)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        followed=user_to_follow
    )
    
    if not created:
        follow.delete()
        is_following = False
        action = 'unfollowed'
    else:
        is_following = True
        action = 'followed'
    
    return JsonResponse({
        'status': action,
        'is_following': is_following,
        'followers_count': user_to_follow.followers.count(),
        'username': user_to_follow.username  # Añadimos username para la notificación
    })

@login_required
def get_follow_status(request, user_id):
    """Obtener estado de seguimiento (AJAX)"""
    user = get_object_or_404(User, id=user_id)
    is_following = Follow.objects.filter(
        follower=request.user,
        followed=user
    ).exists()
    
    return JsonResponse({
        'is_following': is_following,
        'followers_count': user.followers.count(),
        'following_count': user.following.count()
    })