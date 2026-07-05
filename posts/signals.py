from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Post, Comentario
import asyncio

User = get_user_model()

# Simulación simple de notificaciones
# En producción, usarías WebSockets o un modelo de Notificaciones

@receiver(post_save, sender=Post)
def notify_followers_new_post(sender, instance, created, **kwargs):
    """Notificar a seguidores cuando se crea un nuevo post"""
    if not created:
        return
    
    from .models import Follow
    print(f"📢 Nuevo post de {instance.autor.username}: {instance.contenido[:50]}...")

@receiver(post_save, sender=Comentario)
def notify_post_owner_new_comment(sender, instance, created, **kwargs):
    """Notificar al autor del post cuando alguien comenta"""
    if not created:
        return
    
    if instance.autor == instance.post.autor:
        return
    
    print(f"💬 {instance.autor.username} comentó el post de {instance.post.autor.username}")