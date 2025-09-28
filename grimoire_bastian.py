#!/usr/bin/env python3
"""
Script pour générer le grimoire personnalisé de Bastian
"""

from spell_book import SpellPDFGenerator

def main():
    # Génère le grimoire personnalisé de Bastian
    print("🧙‍♂️ Génération du grimoire de Bastian...")
    generator = SpellPDFGenerator(player="bastian")
    
    # Utilise automatiquement le grimoire_title comme nom de fichier
    generator.generate_player_grimoire()
    
    print("✅ Grimoire de Bastian généré avec succès !")
    print(f"📄 Fichier créé : {generator._sanitize_filename(generator.player.get_grimoire_title())}.pdf")

if __name__ == "__main__":
    main()