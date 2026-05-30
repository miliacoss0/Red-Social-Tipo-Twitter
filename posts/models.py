from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Post(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    contenido = models.TextField(max_length=280)
    fecha = models.DateTimeField(auto_now_add=True)
    editado = models.BooleanField(default=False)  # marca si fue editado
    fecha_edicion = models.DateTimeField(null=True, blank=True)  # cuándo se editó
    
    def puede_editar(self):
        # Devuelve True si no pasaron 20 minutos desde que se publicó
        return timezone.now() < self.fecha + timedelta(minutes=20)

    def __str__(self):
        return f"{self.autor.username}: {self.contenido[:50]}"

class Follow(models.Model):
    seguidor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='siguiendo')
    seguido = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seguidores')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seguidor', 'seguido')   #Evita que el mismo usuario siga dos veces a la misma persona.

    def __str__(self):
        return f"{self.seguidor.username} sigue a {self.seguido.username}"