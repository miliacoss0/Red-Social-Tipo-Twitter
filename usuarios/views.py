from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    """
    Página de login.
    Si el usuario ya está logueado, redirige al feed.
    """
    if request.user.is_authenticated:
        return redirect('/feed/')  # ← Redirige directamente al feed
    return render(request, 'login.html')


@login_required
def perfil(request):
    return render(request, 'perfil.html', {'usuario': request.user})
