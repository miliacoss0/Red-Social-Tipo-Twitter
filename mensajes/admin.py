from django.contrib import admin
from .models import Conversacion, Mensaje

@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'creado', 'actualizado']
    filter_horizontal = ['participantes']
    readonly_fields = ['creado', 'actualizado']

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['id', 'emisor', 'contenido', 'fecha_envio', 'leido']
    list_filter = ['leido', 'fecha_envio']
    search_fields = ['contenido', 'emisor__username']
    readonly_fields = ['fecha_envio', 'fecha_leido']