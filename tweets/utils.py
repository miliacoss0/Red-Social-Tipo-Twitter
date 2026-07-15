import re  # Expresiones regulares para buscar patrones en texto
from django.contrib.auth.models import User

#Extraer hashtags de un texto
def extract_hashtags(text):
    """
    Extrae todos los hashtags de un texto.
    Ejemplo: "Hola #python y #django" → ["python", "django"]
    
    ¿Cómo funciona?
    - r'#(\w+)' es una expresión regular
    - # busca el símbolo de numeral
    - (\w+) captura letras, números y guiones bajos que siguen al #
    - re.findall devuelve una lista con todas las coincidencias
    """
    hashtags = re.findall(r'#(\w+)', text)
    # Convertir a minúsculas para evitar duplicados (#Python vs #python)
    return [tag.lower() for tag in hashtags]


#Extraer menciones de un texto
def extract_mentions(text):
    """Extrae todos los nombres de usuario mencionados en un texto"""
    # CAMBIADO: \w+ -> [\w\-]+ para aceptar guiones
    pattern = r'@([\w\-]+)'
    mentions = re.findall(pattern, text)
    return list(set(mentions))

def get_mentioned_users(text):
    """
    Obtiene los objetos User de las menciones en un texto
    """
    usernames = extract_mentions(text)
    users = []
    for username in usernames:
        try:
            user = User.objects.get(username=username)
            users.append(user)
        except User.DoesNotExist:
            pass
    return users