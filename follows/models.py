from django.db import models
from django.conf import settings
from django.utils import timezone

class Follow(models.Model):
    """Modelo para gestionar seguidores"""
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'followed']
        indexes = [
            models.Index(fields=['follower', 'followed']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} sigue a {self.followed.username}"