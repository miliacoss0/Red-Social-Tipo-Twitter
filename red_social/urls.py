from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # ============ NUEVO: URLs para autenticación con GitHub ============
    # Esto añade las siguientes URLs automáticamente:
    # /accounts/login/         → Página de inicio de sesión
    # /accounts/logout/        → Cerrar sesión
    # /accounts/github/login/  → Iniciar sesión con GitHub
    path('accounts/', include('allauth.urls')),               # Login con GitHub

    # ============ NUEVO: URLs de tu app usuarios ============
    path('', include('usuarios.urls')),

    #---- Agregamos la URL de tweets ----
    path('feed/', include('tweets.urls')),                          # Página de feed (tweets)
]
