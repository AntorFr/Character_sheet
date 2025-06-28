import os
from dotenv import load_dotenv
from character_sheet import SpellSheetGenerator

# Charger les variables d'environnement depuis .env
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Vérification que la clé est bien présente
if not API_KEY:
    raise ValueError("Clé API OpenAI manquante. Ajoutez-la dans le fichier .env sous OPENAI_API_KEY.")

# Liste des sorts à générer
sorts = [
    "Contact Glacial", "Glas funèbres", "Lumière", "Message", "Absorption des éléments",
    "Armure de mage", "Bouclier", "Compréhension des langues", "Détection de la magie",
    "Projectile magique", "Rayon empoisonné", "Simulacre de vie", "Vague tonnante",
    "Cécité/Surdité", "Foulée brumeuse", "Immobilisation de personne", "Sphère de feu",
    "Animation des morts", "Boule de feu", "Communication avec les morts",
    "Convocation de mort-vivant", "Contresort", "Toucher du vampire", "Préservation des morts",
    "Disque flottant de Tenser", "Mort simulée"
]

# Initialiser le générateur
generator = SpellSheetGenerator(api_key=API_KEY, output_dir="fiches_sorts")

# Générer tous les sorts
generator.generate_spell_files(sorts)