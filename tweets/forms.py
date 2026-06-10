from django import forms
from .models import Tweet


class TweetForm(forms.ModelForm):
    """
    Formulario para crear/editar tweets.
    """
    class Meta:
        model = Tweet
        # Solo el contenido, el autor lo asignamos automáticamente
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '¿Qué está pasando? Usa #hashtags y @menciones',
                'rows': 3,
                'maxlength': 280,  # Límite de caracteres
                'style': 'width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #ccc;'
            }),
        }
        labels = {
            'content': 'Escribe tu tweet:'
        }