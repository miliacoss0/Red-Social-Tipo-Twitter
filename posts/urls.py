from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('feed/', views.feed, name='feed'),
    path('crear/', views.crear_post, name='crear_post'),
    path('seguir/<int:user_id>/', views.seguir, name='seguir'),
    path('dejar-de-seguir/<int:user_id>/', views.dejar_de_seguir, name='dejar_de_seguir'),
    path('editar/<int:post_id>/', views.editar_post, name='editar_post'),
    path('borrar/<int:post_id>/', views.borrar_post, name='borrar_post'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('hashtags/', views.hashtags, name='hashtags'),
    path('menciones/', views.menciones, name='menciones'),
    path('hashtags/<str:tema>/', views.hashtag_detalle, name='hashtag_detalle'),
    path('api/feed/', views.api_feed, name='api_feed'),
    path('api/session/', views.api_session_info, name='api_session'),
    path('api/borrar/<int:post_id>/', views.api_borrar_post, name='api_borrar_post'),
]