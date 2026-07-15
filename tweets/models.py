from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import extract_hashtags, extract_mentions

# MODELO: HashTag (Almacena los #hashtags)
class HashTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return f"#{self.name}"
    
    class Meta:
        ordering = ['name']



# MODELO: Mention (DEBE ESTAR ANTES DE TWEET)
class Mention(models.Model):
    """
    Modelo para almacenar menciones (@usuario)
    """
    tweet = models.ForeignKey('Tweet', on_delete=models.CASCADE, related_name='menciones')
    mentioned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='menciones_recibidas')
    mentioned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='menciones_hechas')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"@{self.mentioned_by.username} mencionó a @{self.mentioned_user.username}"
    
    class Meta:
        ordering = ['-created_at']


# MODELO: Tweet (Almacena los tweets/publicaciones)
class Tweet(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tweets'
    )
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    hashtags = models.ManyToManyField(HashTag, blank=True, related_name='tweets')
    
    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}..."
    
    def get_mentions(self):
        """
        Devuelve una lista de usuarios mencionados en el tweet
        """
        from .utils import extract_mentions
        mention_names = extract_mentions(self.content)
        mentioned_users = []
        for username in mention_names:
            try:
                user = User.objects.get(username=username)
                mentioned_users.append(user)
            except User.DoesNotExist:
                pass
        return mentioned_users
    
    class Meta:
        ordering = ['-created_at']
    
    # ============================================================
    # MÉTODO SAVE: Procesa hashtags y menciones
    # ============================================================
    def save(self, *args, **kwargs):
        # Guardar el tweet primero
        super().save(*args, **kwargs)
        
        # ========== PROCESAR HASHTAGS ==========
        hashtag_names = extract_hashtags(self.content)
        for name in hashtag_names:
            hashtag, created = HashTag.objects.get_or_create(name=name)
            self.hashtags.add(hashtag)
        
        # Limpiar hashtags que ya no están
        current_hashtag_names = [tag.name.lower() for tag in self.hashtags.all()]
        for hashtag in self.hashtags.all():
            if hashtag.name.lower() not in hashtag_names:
                self.hashtags.remove(hashtag)
        
        # ========== PROCESAR MENCIONES ==========
        mention_names = extract_mentions(self.content)
        for username in mention_names:
            try:
                mentioned_user = User.objects.get(username=username)
                Mention.objects.get_or_create(
                    tweet=self,
                    mentioned_user=mentioned_user,
                    mentioned_by=self.author
                )
                print(f"📢 {self.author.username} mencionó a @{username}")
            except User.DoesNotExist:
                pass


# MODELO: Comentario (Para comentar en tweets)
class Comentario(models.Model):
    """
    Modelo para almacenar comentarios en los tweets
    """
    tweet = models.ForeignKey('Tweet', on_delete=models.CASCADE, related_name='comentarios')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios')
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comentario de {self.author.username} en tweet {self.tweet.id}"
    
    class Meta:
        ordering = ['-created_at']  


# MODELO: Follow (Para seguir usuarios)
class Follow(models.Model):
    """
    Modelo para almacenar relaciones de seguimiento entre usuarios
    """
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'      #Usuarios que sigue
    )
    followed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'   #Usuarios que te siguen
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        #Un usuario no puede seguir al mismo usuario 2 veces
        unique_together = ('follower', 'followed')
        ordering = ['-created_at']
    
    def __str__(self):
        return f" {self.follower.username} sigue a {self.followed.username} "
