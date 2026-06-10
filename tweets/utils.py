import re  # Expresiones regulares para buscar patrones en texto

# ============================================================
# FUNCIÓN: Extraer hashtags de un texto
# ============================================================
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


# ============================================================
# FUNCIÓN: Extraer menciones de un texto
# ============================================================
def extract_mentions(text):
    """
    Extrae todas las menciones de un texto.
    Ejemplo: "Hola @juan y @maria" → ["juan", "maria"]
    
    ¿Cómo funciona?
    - r'@(\w+)' busca el símbolo @ seguido de letras/números
    """
    mentions = re.findall(r'@(\w+)', text)
    return [mention.lower() for mention in mentions]