import json
import os
from typing import Dict, Any, List
from .theme_manager import ThemeManager

class PlayerManager:
    """Gestionnaire des configurations individuelles des joueurs"""
    
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.player_path = f"players/{player_name}"
        self.config = self.load_config()
        self.theme = ThemeManager(self.config["theme"])
        
    def load_config(self) -> Dict[str, Any]:
        """Charge la configuration du joueur depuis le fichier JSON"""
        config_path = f"{self.player_path}/config.json"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration du joueur '{self.player_name}' non trouvée: {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_known_spells(self) -> List[str]:
        """Retourne la liste des sorts connus par le joueur"""
        return self.config.get("known_spells", [])
        
    def get_max_prepared_spells(self) -> int:
        """Retourne le nombre maximum de sorts que le joueur peut préparer"""
        return self.config.get("max_prepared_spells", self.theme.get_max_prepared_spells())
        
    def get_grimoire_title(self) -> str:
        """Retourne le titre personnalisé du grimoire du joueur"""
        return self.config.get("grimoire_title", self.theme.get_title())
    
    def get_character_name(self) -> str:
        """Retourne le nom du personnage"""
        return self.config.get("character_name", self.player_name)
        
    def should_include_spell(self, spell_name: str) -> bool:
        """Détermine si un sort doit être inclus dans le grimoire de ce joueur"""
        known_spells = self.get_known_spells()
        if not known_spells:  # Si pas de liste spécifique, utiliser le filtre du thème
            return self.theme.should_include_spell(spell_name)
        return spell_name in known_spells
    
    def get_custom_overrides(self) -> Dict[str, Any]:
        """Retourne les surcharges personnalisées du joueur"""
        return self.config.get("custom_overrides", {})