from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.home, name='feed_home'),     # Feed de tweets
    
    # Buscador
    path('buscar/', views.search, name='search'),
    
    # Página de hashtag 
    path('tag/<str:tag_name>/', views.hashtag_view, name='hashtag'),

    # Menciones
    path('menciones/<int:id>/', views.mis_menciones, name='menciones'),

    # tweet_detalle
    path('tweet/<int:tweet_id>/', views.tweet_detalle, name='tweet_detalle'), 

    # Perfil de usuario
    path('perfil/<str:username>/', views.perfil_usuario, name='perfil_usuario'), 

    # hashtags populares 
    path('hashtags/', views.hashtags_populares, name='hashtags_populares'),

    # comentarios 
    path('comentarios/<int:tweet_id>', views.comentarios, name='comentarios'),
]
    