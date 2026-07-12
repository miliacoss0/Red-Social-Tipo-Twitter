from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.conf import settings

class Post(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    contenido = models.TextField(max_length=280)
    fecha = models.DateTimeField(auto_now_add=True)
    editado = models.BooleanField(default=False)  # marca si fue editado
    fecha_edicion = models.DateTimeField(null=True, blank=True)  # cuándo se editó
    imagen = models.ImageField(upload_to='posts/', null=True, blank=True)  
    archivo = models.FileField(upload_to='posts/archivos/', null=True, blank=True)
    
    def puede_editar(self):
        # Devuelve True si no pasaron 20 minutos desde que se publicó
        return timezone.now() < self.fecha + timedelta(minutes=20)

    def __str__(self):
        return f"{self.autor.username}: {self.contenido[:50]}"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Invalidar cache del feed
        try:
            cache.delete(f'feed_user_{self.autor.id}_page_1')
        except Exception:
            pass
    
    def delete(self, *args, **kwargs):
        autor_id = self.autor.id
        super().delete(*args, **kwargs)
        try:
            cache.delete(f'feed_user_{autor_id}_page_1')
        except Exception:
            pass

class Follow(models.Model):
    seguidor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='siguiendo')
    seguido = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seguidores')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seguidor', 'seguido')   #Evita que el mismo usuario siga dos veces a la misma persona.

    def __str__(self):
        return f"{self.seguidor.username} sigue a {self.seguido.username}"

class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenido = models.TextField(max_length=500)
    fecha = models.DateTimeField(auto_now_add=True)
    editado = models.BooleanField(default=False)
    fecha_edicion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return f"{self.autor.username} -> {self.post.id}"

    def puede_editar(self):
        return (timezone.now() - self.fecha) < timedelta(minutes=5)


class MentionPost(models.Model):
    """Modelo para almacenar menciones (@usuario) en POSTS"""
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='menciones_post')
    mentioned_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='menciones_post_recibidas')
    mentioned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='menciones_post_hechas')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"@{self.mentioned_by.username} mencionó a @{self.mentioned_user.username} en un post"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mención en Post'
        verbose_name_plural = 'Menciones en Posts'