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
    path('api/nuevos-posts/', views.api_nuevos_posts, name='api_nuevos_posts'),
    path('api/hashtags/', views.api_hashtags, name='api_hashtags'),
    path('api/hashtags/<str:tema>/', views.api_hashtag_detalle, name='api_hashtag_detalle'),
    path('like/<int:post_id>/', views.like_toggle, name='like_toggle'),
    path('api/like/<int:post_id>/', views.api_like_toggle, name='api_like_toggle'),
    path('comentar/<int:post_id>/', views.comentar_post, name='comentar_post'),
    path('api/comentarios/<int:post_id>/', views.api_comentarios, name='api_comentarios'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
    path('api/notificaciones/', views.api_notificaciones, name='api_notificaciones'),
]