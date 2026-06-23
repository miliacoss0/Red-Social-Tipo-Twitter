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
    path('api/seguir/<int:user_id>/', views.api_seguir, name='api_seguir'),
    path('api/dejar-de-seguir/<int:user_id>/', views.api_dejar_de_seguir, name='api_dejar_de_seguir'),
    path('api/editar/<int:post_id>/', views.api_editar_post, name='api_editar_post'),
    path('api/usuarios/', views.api_usuarios, name='api_usuarios'),
    path('api/hashtags/', views.api_hashtags, name='api_hashtags'),
    path('api/hashtags/<str:tema>/', views.api_hashtag_detalle, name='api_hashtag_detalle'),
    path('api/menciones/', views.api_menciones, name='api_menciones'),
]