from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

def home(request):
    """
    Vista principal que muestra contenido diferente
    si el usuario está autenticado o no
    """
    return render(request, 'home.html')

@login_required  # Solo usuarios autenticados pueden ver esta vista
def perfil(request):
    """
    Vista del perfil del usuario con información de GitHub
    """
    contexto = {
        'usuario': request.user,
    }
    return render(request, 'perfil.html', contexto)
