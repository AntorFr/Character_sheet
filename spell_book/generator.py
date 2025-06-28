import os
import json
import requests

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

from .illustrations import SpellIllustrationGenerator
from character_sheet.utils import sanitize_filename

# Constantes de mise en page et style
FONT_SIZE_TITLE = 20
FONT_SIZE_SUBTITLE = 12
FONT_SIZE_BODY = 11
LINE_HEIGHT_BODY = 14

COLOR_TITLE = colors.darkred
COLOR_SUBTITLE = colors.slategrey
COLOR_BODY = colors.black

# Marges et espacements
MARGIN_LEFT = 1.0 * cm
MARGIN_RIGHT = 1.0 * cm
MARGIN_TOP = 0.8 * cm
MARGIN_BOTTOM = 0.8 * cm
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

    def generate_compiled_pdf(self, folder_path: str, output_path: str = "grimoire_complet.pdf"):
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
        illustrateur = SpellIllustrationGenerator(api_key=os.getenv("OPENAI_API_KEY"))
        image_path = illustrateur.generate_illustration(spell["Nom"], spell.get("Description complète", ""))

        title_para = Paragraph(titre, styles["Titre"])
        if image_path and os.path.exists(image_path):
            img = Image(image_path, width=90, height=90)
            title_table = Table([[title_para, img]], colWidths=[None, 2.5*cm])
            title_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "RIGHT"),
                ("VALIGN", (1, 0), (1, 0), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ]))
        else:
            title_table = Table([[title_para]], colWidths=[10.5*cm])

        story.append(title_table)
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
            story.append(Spacer(1, SPACER_SMALL))
            story.append(Paragraph("<b>Effet en surcaste :</b>", styles["SousTitre"]))
            story.append(Paragraph(effet_surcaste, styles["Corps"]))

        story.append(PageBreak())

    def _ajouter_info(self, story, label, valeur, styles):
        if valeur:
            story.append(Paragraph(
                f"<font color='slategrey'><b>{label} :</b></font> {valeur}",
                styles["Corps"]
            ))


