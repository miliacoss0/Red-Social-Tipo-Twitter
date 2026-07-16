from django.urls import path
from . import views

app_name = 'mensajes'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('conversacion/<int:usuario_id>/', views.conversacion, name='conversacion'),
    path('api/enviar/', views.api_enviar_mensaje, name='api_enviar_mensaje'),
    path('api/mensajes/<int:conversacion_id>/', views.api_obtener_mensajes, name='api_obtener_mensajes'),
    path('api/marcar-leido/<int:mensaje_id>/', views.api_marcar_leido, name='api_marcar_leido'),
    path('api/conversaciones/', views.api_conversaciones, name='api_conversaciones'),
]