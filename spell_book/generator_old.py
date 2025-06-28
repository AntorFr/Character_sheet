import os
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

# Constantes de mise en page et style
FONT_SIZE_TITLE = 20
FONT_SIZE_SUBTITLE = 12
FONT_SIZE_BODY = 11
LINE_HEIGHT_BODY = 14

COLOR_TITLE = colors.darkred
COLOR_SUBTITLE = colors.slategrey
COLOR_BODY = colors.black

# Marges et espacements

SPACER_SMALL = 6
SPACER_MEDIUM = 8
SPACER_LARGE = 10

class SpellPDFGenerator:
    def __init__(self, font_path: str, output_dir: str = "pdf_sorts"):
        self.font_name = "Manuscrite"
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        pdfmetrics.registerFont(TTFont(self.font_name, font_path))
        self.font_name_title = "TitreMagique"
        pdfmetrics.registerFont(TTFont(self.font_name_title, "fonts/CaesarDressing-Regular.ttf"))

    def generate_from_file(self, json_path: str):
        with open(json_path, encoding='utf-8') as f:
            spell = json.load(f)
        spell_name = spell["Nom"].replace(" ", "_") + ".pdf"
        output_path = os.path.join(self.output_dir, spell_name)
        self._create_pdf(spell, output_path)

    def generate_from_folder(self, folder_path: str):
        for file in os.listdir(folder_path):
            if file.endswith(".json"):
                self.generate_from_file(os.path.join(folder_path, file))

    def _create_pdf(self, spell: dict, output_path: str):
        c = canvas.Canvas(output_path, pagesize=A5)
        c.setFont(self.font_name, 12)

        margin_x = 1.5 * cm
        margin_y = 1.5 * cm
        width, height = A5
        x = margin_x
        y = height - margin_y

        def draw_line(label, value, space=14):
            nonlocal y
            if value:
                c.drawString(x, y, f"{label} : {value}")
                y -= space

        c.setFont(self.font_name, 18)
        c.drawCentredString(width / 2, y, spell["Nom"])
        y -= 22
        c.setFont(self.font_name, 12)

        draw_line("Nom original", spell.get("Nom original"))
        draw_line("Niveau", spell.get("Niveau"))
        draw_line("École", spell.get("École"))
        draw_line("Temps d'incantation", spell.get("Temps d'incantation"))
        draw_line("Portée", spell.get("Portée"))
        draw_line("Cible", spell.get("Cible"))
        draw_line("Composantes", spell.get("Composantes"))
        draw_line("Durée", spell.get("Durée"))
        draw_line("Concentration", "Oui" if spell.get("Concentration") else "Non")
        draw_line("Rituel", spell.get("Rituel"))
        draw_line("Type", spell.get("Type d'attaque / sauvegarde"))

        y -= 10
        c.drawString(x, y, "Description :")
        y -= 14

        for line in spell.get("Description complète", "").split(". "):
            if y < margin_y + 40:
                c.showPage()
                y = height - margin_y
                c.setFont(self.font_name, 12)
            c.drawString(x, y, line.strip())
            y -= 14

        c.save()

    def generate_compiled_pdf(self, folder_path: str, output_path: str = "grimoire_complet.pdf"):
        MARGIN_LEFT = 1.0 * cm
        MARGIN_RIGHT = 1.0 * cm
        MARGIN_TOP = 0.8 * cm
        MARGIN_BOTTOM = 0.8 * cm
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Titre', fontName=self.font_name_title, fontSize=FONT_SIZE_TITLE, alignment=TA_CENTER, spaceAfter=12, textColor=COLOR_TITLE))
        styles.add(ParagraphStyle(name='SousTitre', fontName=self.font_name, fontSize=FONT_SIZE_SUBTITLE, alignment=TA_LEFT, spaceAfter=6, textColor=COLOR_SUBTITLE))
        styles.add(ParagraphStyle(name='Corps', fontName=self.font_name, fontSize=FONT_SIZE_BODY, alignment=TA_LEFT, leading=LINE_HEIGHT_BODY, textColor=COLOR_BODY))

        story = []
        fichiers = sorted(os.listdir(folder_path))

        for file in fichiers:
            if not file.endswith(".json") or file == "index.json":
                continue
            with open(os.path.join(folder_path, file), encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for spell in data:
                        self._append_spell_to_story(spell, story, styles)
                else:
                    self._append_spell_to_story(data, story, styles)

        doc = SimpleDocTemplate(output_path, pagesize=A5,
                                leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
                                topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM)
        doc.build(story)

    def _append_spell_to_story(self, spell: dict, story: list, styles):
        titre = spell.get("Nom", "Sort inconnu")
        story.append(Paragraph(titre, styles["Titre"]))
        story.append(Spacer(1, SPACER_MEDIUM))

        portee = spell.get("Portée", "-")
        if isinstance(portee, int) or (isinstance(portee, str) and portee.isdigit()):
            portee = f"{portee} mètres"

        headers = ["Niveau", "École", "Rituel"]
        values1 = [spell.get("Niveau", "-"), spell.get("École", "-"), spell.get("Rituel", "-")]
        headers2 = ["Temps", "Portée", "Concentration"]
        values2 = [spell.get("Temps d'incantation", "-"), portee, "Oui" if spell.get("Concentration") else "Non"]

        table_data = [headers, values1, headers2, values2]
        table = Table(table_data, colWidths=[5*cm]*3)
        table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.slategrey),
            ('TEXTCOLOR', (0, 2), (-1, 2), colors.slategrey),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # 'TEXTCOLOR', (0, 0), (-1, -1), colors.black  # supprimé pour laisser les couleurs spécifiques agir
        ]))
        story.append(table)
        story.append(Spacer(1, SPACER_LARGE))

        

        self._ajouter_info(story, "Type", spell.get("Type d'attaque / sauvegarde"), styles)
        self._ajouter_info(story, "Cible", spell.get("Cible"), styles)
        self._ajouter_info(story, "Composantes", spell.get("Composantes"), styles)

        story.append(Spacer(1, SPACER_SMALL))
        story.append(Paragraph("<b>Description :</b>", styles["SousTitre"]))
        story.append(Paragraph(spell.get("Description complète", ""), styles["Corps"]))

        effet_surcaste = spell.get("Effet en surcaste")
        if effet_surcaste:
            story.append(Spacer(1, 6))
            story.append(Paragraph("<b>Effet en surcaste :</b>", styles["SousTitre"]))
            story.append(Paragraph(effet_surcaste, styles["Corps"]))
        story.append(PageBreak())

    def _ajouter_info(self, story, label, valeur, styles):
        if valeur:
            story.append(Paragraph(
                f"<font color='slategrey'><b>{label} :</b></font> {valeur}",
                styles["Corps"]
            ))
