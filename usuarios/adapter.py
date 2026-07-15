from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Adaptador personalizado para manejar usuarios de GitHub"""
    
    def populate_user(self, request, sociallogin, data):
        """
        Asegurar que siempre haya un username válido
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Si el username está vacío, generarlo del email
        if not user.username:
            email = data.get('email', '')
            if email:
                # Usar parte del email como username
                user.username = email.split('@')[0]
            else:
                # Si no hay email, usar el nombre de GitHub
                user.username = data.get('login', '') or data.get('name', '').replace(' ', '_').lower()
        
        # Si el username aún está vacío, generar uno único
        if not user.username:
            base_username = 'github_user'
            counter = 1
            username = base_username
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            user.username = username
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Guardar usuario asegurando username único
        """
        user = super().save_user(request, sociallogin, form)
        
        # Si el username está vacío después de guardar, corregirlo
        if not user.username:
            email = user.email or ''
            if email:
                username = email.split('@')[0]
            else:
                username = f"user_{user.id}"
            
            # Asegurar unicidad
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user.username = username
            user.save(update_fields=['username'])
        
        return user