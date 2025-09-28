#!/usr/bin/env python3
"""
Script pour générer un grimoire basé sur le thème nécromancien
"""

from spell_book import SpellPDFGenerator

def main():
    # Génère le grimoire basé sur le thème nécromancien
    print("🎭 Génération du grimoire thème nécromancien...")
    generator = SpellPDFGenerator(theme="necromancien")
    generator.generate_theme_grimoire("Grimoire_Theme_Necromancien.pdf")
    
    print("✅ Grimoire thème nécromancien généré avec succès !")
    print("📄 Fichier créé : Grimoire_Theme_Necromancien.pdf")

if __name__ == "__main__":
    main()