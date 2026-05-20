"""
URL configuration for red_social project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # ============ NUEVO: URLs para autenticación con GitHub ============
    # Esto añade las siguientes URLs automáticamente:
    # /accounts/login/         → Página de inicio de sesión
    # /accounts/logout/        → Cerrar sesión
    # /accounts/github/login/  → Iniciar sesión con GitHub
    path('accounts/', include('allauth.urls')),

    # ============ NUEVO: URLs de tu app usuarios ============
    path('', include('usuarios.urls')),
]
