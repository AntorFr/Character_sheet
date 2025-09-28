#!/usr/bin/env python3
"""
Script pour générer le grimoire personnalisé de Fadette (Elf des Bois)
"""

from spell_book import SpellPDFGenerator

def main():
    # Génère le grimoire personnalisé de Fadette
    print("🧚‍♀️ Génération du grimoire de Fadette (Elf des Bois)...")
    generator = SpellPDFGenerator(player="fadette")
    
    # Utilise automatiquement le grimoire_title comme nom de fichier
    generator.generate_player_grimoire()
    
    print("✅ Grimoire de Fadette généré avec succès !")
    print(f"📄 Fichier créé : {generator._sanitize_filename(generator.player.get_grimoire_title())}.pdf")

if __name__ == "__main__":
    main()