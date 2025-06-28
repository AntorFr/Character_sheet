from spell_book import SpellPDFGenerator

generator = SpellPDFGenerator(font_path="fonts/HomemadeApple-Regular.ttf")
generator.generate_compiled_pdf("fiches_sorts", output_path="Grimoire_du_Necromancien.pdf")
