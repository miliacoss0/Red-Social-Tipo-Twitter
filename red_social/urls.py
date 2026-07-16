from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from mensajes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('usuarios.urls')),
    #URL de tweet
    path('feed/', include('tweets.urls')),                          # Página de feed (tweets)
    #URLs de tu app post 
    path('posts/', include('posts.urls')),   
    path('tweets/', include('tweets.urls')), 
    path('mensajes/', include('mensajes.urls')),
    path('api/conversaciones/', views.api_conversaciones),
    path('follows/', include('follows.urls')), 
]

#Archivo multimedia en modo desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


