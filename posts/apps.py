from django.apps import AppConfig

class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts'
    verbose_name = 'Publicaciones'
    
    def ready(self):
        import posts.signals  # Registrar señales