import re
import unicodedata

def sanitize_filename(name: str) -> str:
    # 1. Supprimer les accents
    name = unicodedata.normalize("NFD", name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn') 
    # 2. Supprimer les caractères interdits pour un nom de fichier
    name = re.sub(r'[\\/:"*?<>|]', '', name)
    # 3. Remplacer les espaces et tirets par des underscores
    name = re.sub(r'\s+', '_', name)
    
    # 4. Mettre en minuscules
    return name.lower()