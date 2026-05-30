from django.urls import path
from . import views

urlpatterns = [
    # Página principal (home) después del login
    path('', views.home, name='home'),
    
    # Página de perfil de usuario
    path('perfil/', views.perfil, name='perfil'),
]