from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.home, name='feed_home'),     # Feed de tweets
    
    # Buscador
    path('buscar/', views.search, name='search'),
    
    # Página de hashtag 
    path('tag/<str:tag_name>/', views.hashtag_view, name='hashtag'),

    # Menciones
    path('menciones/', views.mis_menciones, name='mis_menciones'),

    # tweet_detalle
    path('tweet/<int:tweet_id>/', views.tweet_detalle, name='tweet_detalle'), 

    # Perfil de usuario
    path('perfil/<str:username>/', views.perfil_usuario, name='perfil_usuario'), 

    # API endpoints
    path('api/tweets/', views.api_tweets, name='api_tweets'),
    path('api/tweets/usuario/<str:username>/', views.api_tweets_usuario, name='api_tweets_usuario'), 
    path('api/tweets/hashtag/<str:tag_name>/', views.api_tweets_hashtag, name='api_tweets_hashtag'),  
    path('api/menciones/', views.api_mis_menciones, name='api_mis_menciones'),  
    path('api/buscar/', views.api_buscar_tweets, name='api_buscar_tweets'),  
    path('api/session/', views.api_session_info, name='api_session_tweets'), 

    #leido
    path('api/marcar-leida/<int:mencion_id>/', views.api_marcar_mencion_leida, name='api_marcar_mencion_leida'), 
]