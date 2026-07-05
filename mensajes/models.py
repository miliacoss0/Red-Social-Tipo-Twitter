from django.db import models
from django.conf import settings
from django.utils import timezone

class Conversacion(models.Model):
    """Conversación entre usuarios"""
    participantes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversaciones'
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-actualizado']
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'

    def __str__(self):
        usuarios = list(self.participantes.all()[:2])
        return f"Conversación entre {', '.join([u.username for u in usuarios])}"

    def obtener_ultimo_mensaje(self):
        return self.mensajes.order_by('-fecha_envio').first()


class Mensaje(models.Model):
    """Mensaje directo"""
    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.CASCADE,
        related_name='mensajes'
    )
    emisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados'
    )
    contenido = models.TextField(max_length=1000)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    fecha_leido = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['fecha_envio']
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'

    def __str__(self):
        return f"Mensaje de {self.emisor.username}"

    def marcar_como_leido(self):
        if not self.leido:
            self.leido = True
            self.fecha_leido = timezone.now()
            self.save()