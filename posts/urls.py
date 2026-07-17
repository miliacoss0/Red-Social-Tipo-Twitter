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
    path('menciones/', views.todas_menciones, name='menciones'),
    path('hashtags/<str:tema>/', views.hashtag_detalle, name='hashtag_detalle'),
    
    #URLs API
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
    path('api/nuevos-posts/', views.api_nuevos_posts, name='api_nuevos_posts'),
    path('api/like/<int:post_id>/', views.api_like_toggle, name='api_like_toggle'),
    path('api/comentarios/<int:post_id>/', views.api_comentarios, name='api_comentarios'),
    path('api/notificaciones/', views.api_notificaciones, name='api_notificaciones'),
    path('api/menciones-posts/', views.api_mis_menciones_posts, name='api_mis_menciones_posts'),
    path('api/menciones-posts/marcar-leida/<int:mencion_id>/', views.api_marcar_menciom_post_leida, name='api_marcar_menciom_post_leida'),
    path('api/contador-menciones/', views.api_contador_menciones, name='api_contador_menciones'),
    path('api/comentarios/editar/<int:comentario_id>/', views.api_editar_comentario, name='api_editar_comentario'),
    path('api/comentarios/eliminar/<int:comentario_id>/', views.api_eliminar_comentario, name='api_eliminar_comentario'),
    
    #URLs HTML
    path('like/<int:post_id>/', views.like_toggle, name='like_toggle'),
    path('comentar/<int:post_id>/', views.comentar_post, name='comentar_post'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
    
    #likes
    path('api/like/<int:post_id>/', views.api_like_toggle, name='api_like_toggle'),
    path('api/likes/<int:post_id>/', views.api_obtener_likes, name='api_obtener_likes'),
]