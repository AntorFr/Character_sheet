import json
import os
from typing import Dict, Any, List

class ThemeManager:
    """Gestionnaire des thèmes pour les grimoires"""
    
    def __init__(self, theme_name: str):
        self.theme_name = theme_name
        self.theme_path = f"themes/{theme_name}"
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Charge la configuration du thème depuis le fichier JSON"""
        config_path = f"{self.theme_path}/config.json"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration du thème '{self.theme_name}' non trouvée: {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_font_path(self, font_type: str) -> str:
        """Retourne le chemin complet vers une police"""
        font_name = self.config["fonts"][font_type]
        return f"fonts/{font_name}"
    
    def get_illustrations_folder(self) -> str:
        """Retourne le dossier des illustrations pour ce thème"""
        return f"{self.theme_path}/illustrations"
    
    def get_illustration_style(self) -> str:
        """Retourne le style d'illustration pour ce thème"""
        return self.config.get("illustration_style", "fantasy art")
    
    def get_colors(self) -> Dict[str, str]:
        """Retourne les couleurs du thème"""
        return self.config.get("colors", {})
    
    def get_title(self) -> str:
        """Retourne le titre du grimoire pour ce thème"""
        return self.config.get("title", "Grimoire")
    
    def get_max_prepared_spells(self) -> int:
        """Retourne le nombre maximum de sorts préparés par défaut"""
        return self.config.get("max_prepared_spells", 10)
    
    def should_include_spell(self, spell_name: str) -> bool:
        """Détermine si un sort doit être inclus dans ce thème"""
        spell_filter = self.config.get("spell_filter", "all")
        if spell_filter == "all":
            return True
        if isinstance(spell_filter, list):
            return any(filter_term.lower() in spell_name.lower() for filter_term in spell_filter)
        return True