from spell_book import SpellPDFGenerator

generator = SpellPDFGenerator(font_path="fonts/HomemadeApple-Regular.ttf")
generator.generate_grimoire_with_table_of_contents("fiches_sorts", output_path="Grimoire_du_Necromancien.pdf")
