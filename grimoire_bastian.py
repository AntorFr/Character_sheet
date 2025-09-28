#!/usr/bin/env python3
"""
Script pour générer le grimoire personnalisé de Bastian
"""

from spell_book import SpellPDFGenerator

def main():
    # Génère le grimoire personnalisé de Bastian
    print("🧙‍♂️ Génération du grimoire de Bastian...")
    generator = SpellPDFGenerator(player="bastian")
    generator.generate_player_grimoire("Grimoire_Bastian.pdf")
    
    print("✅ Grimoire de Bastian généré avec succès !")
    print("📄 Fichier créé : Grimoire_Bastian.pdf")

if __name__ == "__main__":
    main()