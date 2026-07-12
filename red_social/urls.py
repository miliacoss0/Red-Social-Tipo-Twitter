from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from mensajes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('usuarios.urls')),
    path('posts/', include('posts.urls')),
    path('feed/', include('tweets.urls')),
    path('tweets/', include('tweets.urls')), 
    path('mensajes/', include('mensajes.urls')),
    path('api/conversaciones/', views.api_conversaciones),
    path('follows/', include('follows.urls')), 

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)