from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # URLs para autenticación con GitHub 
    # Esto añade las siguientes URLs automáticamente:
    # /accounts/login/         → Página de inicio de sesión
    # /accounts/logout/        → Cerrar sesión
    # /accounts/github/login/  → Iniciar sesión con GitHub
    path('accounts/', include('allauth.urls')),               # Login con GitHub

    #URLs de tu app usuarios
    path('', include('usuarios.urls')),

    #URL de tweet
    path('feed/', include('tweets.urls')),                          # Página de feed (tweets)

    
    #URLs de tu app post 
    path('posts/', include('posts.urls')),   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
