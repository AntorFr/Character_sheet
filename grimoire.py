from spell_book import SpellPDFGenerator

# Nouveau système avec le joueur Bastian
generator = SpellPDFGenerator(player="bastian")
generator.generate_player_grimoire("Grimoire_du_Necromancien.pdf")
