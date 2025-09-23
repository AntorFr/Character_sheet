import os
import json
import requests
from dotenv import load_dotenv

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

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Constantes de mise en page et style
FONT_SIZE_TITLE = 20
FONT_SIZE_SUBTITLE = 12
FONT_SIZE_BODY = 11
LINE_HEIGHT_BODY = 14

COLOR_TITLE = colors.darkred
COLOR_SUBTITLE = colors.slategrey
COLOR_BODY = colors.black

# Marges et espacements
MARGIN_LEFT = 1.2 * cm
MARGIN_RIGHT = 1.0 * cm
MARGIN_TOP = 0.5 * cm
MARGIN_BOTTOM = 1.0 * cm
SPACER_SMALL = 5
SPACER_MEDIUM = 7
SPACER_LARGE = 9

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
        styles.add(ParagraphStyle(name='Titre', fontName=self.font_name_title, fontSize=FONT_SIZE_TITLE, alignment=TA_CENTER, spaceAfter=SPACER_LARGE, textColor=COLOR_TITLE))
        styles.add(ParagraphStyle(name='SousTitre', fontName=self.font_name, fontSize=FONT_SIZE_SUBTITLE, alignment=TA_LEFT, spaceAfter=SPACER_SMALL, textColor=COLOR_SUBTITLE))
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
        
        # Vérifier si une illustration existe déjà
        spell_name_clean = sanitize_filename(titre)
        image_path = f"illustrations/{spell_name_clean}.png"
        
        # Utiliser l'illustration existante si elle existe
        if os.path.exists(image_path):
            print(f"✔ Illustration existante utilisée pour '{titre}': {image_path}")
        # Sinon, générer une illustration seulement si la clé API est disponible
        elif os.getenv("OPENAI_API_KEY"):
            try:
                illustrateur = SpellIllustrationGenerator(api_key=os.getenv("OPENAI_API_KEY"))
                image_path = illustrateur.generate_illustration(spell["Nom"], spell.get("Description complète", ""))
                illustrateur.generate_large_illustration(spell["Nom"], spell.get("Description complète", ""))
                print(f"🎨 Illustration générée pour '{titre}': {image_path}")
            except Exception as e:
                print(f"❌ Impossible de générer l'illustration pour {titre}: {e}")
                image_path = None
        else:
            print(f"⚠ Pas d'illustration disponible pour '{titre}' (pas de clé API)")
            image_path = None

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

        story.append(Spacer(1, SPACER_MEDIUM))
        story.append(Paragraph("<b>Description :</b>", styles["SousTitre"]))
        story.append(Paragraph(spell.get("Description complète", ""), styles["Corps"]))

        effet_surcaste = spell.get("Effet en surcaste")
        if effet_surcaste:
            story.append(Spacer(1, SPACER_MEDIUM))
            story.append(Paragraph("<b>Effet en surcaste :</b>", styles["SousTitre"]))
            story.append(Paragraph(effet_surcaste, styles["Corps"]))

        story.append(PageBreak())

    def generate_table_of_contents(self, folder_path: str, output_path: str = "sommaire_grimoire.pdf"):
        """Génère une page de sommaire avec la liste des sorts organisée par niveau"""
        styles = getSampleStyleSheet()
        
        # Styles personnalisés pour le sommaire
        styles.add(ParagraphStyle(
            name='TitreSommaire', 
            fontName=self.font_name_title, 
            fontSize=24, 
            alignment=TA_CENTER, 
            spaceAfter=20, 
            textColor=COLOR_TITLE
        ))
        styles.add(ParagraphStyle(
            name='NiveauHeader', 
            fontName=self.font_name, 
            fontSize=16, 
            alignment=TA_LEFT, 
            spaceAfter=8, 
            spaceBefore=15,
            textColor=COLOR_SUBTITLE
        ))
        styles.add(ParagraphStyle(
            name='SortEntry', 
            fontName=self.font_name, 
            fontSize=11, 
            alignment=TA_LEFT, 
            spaceAfter=2,
            textColor=COLOR_BODY
        ))

        story = []
        
        # Titre du sommaire
        story.append(Paragraph("Sommaire du Grimoire", styles["TitreSommaire"]))
        story.append(Spacer(1, 15))

        # Lire tous les sorts et les organiser
        sorts_par_niveau = {}
        fichiers = [f for f in os.listdir(folder_path) if f.endswith(".json") and f != "index.json"]
        
        for file in fichiers:
            with open(os.path.join(folder_path, file), encoding='utf-8') as f:
                data = json.load(f)
                # Gestion des fichiers contenant une liste ou un seul sort
                sorts = data if isinstance(data, list) else [data]
                
                for spell in sorts:
                    niveau = spell.get("Niveau", 0)
                    if niveau not in sorts_par_niveau:
                        sorts_par_niveau[niveau] = []
                    sorts_par_niveau[niveau].append(spell)

        # Trier les sorts par niveau, puis par nom
        for niveau in sorted(sorts_par_niveau.keys()):
            sorts_par_niveau[niveau].sort(key=lambda x: x.get("Nom", ""))

        # Générer le contenu du sommaire
        for niveau in sorted(sorts_par_niveau.keys()):
            # En-tête de niveau
            niveau_text = f"Niveau {niveau}" if niveau > 0 else "Tours de magie"
            story.append(Paragraph(f"<b>{niveau_text}</b>", styles["NiveauHeader"]))
            
            # Liste des sorts pour ce niveau
            table_data = []
            for spell in sorts_par_niveau[niveau]:
                nom_sort = spell.get("Nom", "Sort inconnu")
                rituel = spell.get("Rituel", "Non")
                
                # Détermine le symbole : case vide, R pour rituel
                if rituel.lower() in ["oui", "yes", "true"]:
                    symbole = "R"
                else:
                    symbole = "☐"  # Case à cocher vide
                
                # Créer une ligne du tableau
                table_data.append([symbole, nom_sort])
            
            if table_data:
                # Créer le tableau pour ce niveau
                table = Table(table_data, colWidths=[0.8*cm, 12*cm])
                table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), self.font_name_title),  # Police titre pour les symboles
                    ('FONTNAME', (1, 0), (1, -1), self.font_name),        # Police manuscrite pour les noms
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Centrer les symboles
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),    # Aligner les noms à gauche
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                story.append(table)
                story.append(Spacer(1, 10))

        # Créer le PDF
        doc = SimpleDocTemplate(output_path, pagesize=A5,
                                leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
                                topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM)
        doc.build(story)
        print(f"Sommaire généré : {output_path}")

    def generate_grimoire_with_table_of_contents(self, folder_path: str, output_path: str = "grimoire_avec_sommaire.pdf"):
        """Génère un grimoire complet avec sommaire intégré en première page"""
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Titre', fontName=self.font_name_title, fontSize=FONT_SIZE_TITLE, alignment=TA_CENTER, spaceAfter=SPACER_LARGE, textColor=COLOR_TITLE))
        styles.add(ParagraphStyle(name='SousTitre', fontName=self.font_name, fontSize=FONT_SIZE_SUBTITLE, alignment=TA_LEFT, spaceAfter=SPACER_SMALL, textColor=COLOR_SUBTITLE))
        styles.add(ParagraphStyle(name='Corps', fontName=self.font_name, fontSize=FONT_SIZE_BODY, alignment=TA_LEFT, leading=LINE_HEIGHT_BODY, textColor=COLOR_BODY))
        
        # Styles pour le sommaire
        styles.add(ParagraphStyle(
            name='TitreSommaire', 
            fontName=self.font_name_title, 
            fontSize=24, 
            alignment=TA_CENTER, 
            spaceAfter=20, 
            textColor=COLOR_TITLE
        ))
        styles.add(ParagraphStyle(
            name='NiveauHeader', 
            fontName=self.font_name, 
            fontSize=16, 
            alignment=TA_LEFT, 
            spaceAfter=8, 
            spaceBefore=15,
            textColor=COLOR_SUBTITLE
        ))
        styles.add(ParagraphStyle(
            name='SortsPreparesStyle', 
            fontName=self.font_name, 
            fontSize=12, 
            alignment=TA_CENTER, 
            spaceAfter=8,
            textColor=colors.darkblue
        ))

        story = []
        
        # === GÉNÉRATION DU SOMMAIRE ===
        story.append(Paragraph("Carnis Resurrectionem", styles["TitreSommaire"]))
        story.append(Spacer(1, 10))
        
        # Champ pour le nombre de sorts préparés aligné à droite
        sorts_prepares_text = f"Préparable : 10"
        sorts_prepares_table = Table([[sorts_prepares_text]], colWidths=[13*cm])
        sorts_prepares_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), self.font_name),
            ('FONTSIZE', (0, 0), (0, 0), 12),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.darkblue),
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
        ]))
        story.append(sorts_prepares_table)
        story.append(Spacer(1, 15))

        # Lire tous les sorts et les organiser
        sorts_par_niveau = {}
        fichiers = [f for f in sorted(os.listdir(folder_path)) if f.endswith(".json") and f != "index.json"]
        
        for file in fichiers:
            with open(os.path.join(folder_path, file), encoding='utf-8') as f:
                data = json.load(f)
                sorts = data if isinstance(data, list) else [data]
                
                for spell in sorts:
                    niveau = spell.get("Niveau", 0)
                    if niveau not in sorts_par_niveau:
                        sorts_par_niveau[niveau] = []
                    sorts_par_niveau[niveau].append(spell)

        # Trier les sorts par niveau, puis par nom
        for niveau in sorted(sorts_par_niveau.keys()):
            sorts_par_niveau[niveau].sort(key=lambda x: x.get("Nom", ""))

        # Générer le contenu du sommaire
        for niveau in sorted(sorts_par_niveau.keys()):
            niveau_text = f"Niveau {niveau}" if niveau > 0 else "Tours de magie"
            story.append(Paragraph(f"<b>{niveau_text}</b>", styles["NiveauHeader"]))
            
            table_data = []
            for spell in sorts_par_niveau[niveau]:
                nom_sort = spell.get("Nom", "Sort inconnu")
                rituel = spell.get("Rituel", "Non")
                
                if rituel.lower() in ["oui", "yes", "true"]:
                    symbole = "R"
                else:
                    symbole = "O"
                
                table_data.append([symbole, nom_sort])
            
            if table_data:
                table = Table(table_data, colWidths=[0.8*cm, 12*cm])
                table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), self.font_name_title),  # Police titre pour les symboles
                    ('FONTNAME', (1, 0), (1, -1), self.font_name),        # Police manuscrite pour les noms
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ]))
                story.append(table)
                story.append(Spacer(1, 10))

        # Saut de page après le sommaire
        story.append(PageBreak())

        # === GÉNÉRATION DES FICHES DE SORTS ===
        # Réutiliser la logique de la méthode generate_compiled_pdf
        for niveau in sorted(sorts_par_niveau.keys()):
            for spell in sorts_par_niveau[niveau]:
                self._append_spell_to_story(spell, story, styles)

        # Construire le PDF final
        doc = SimpleDocTemplate(output_path, pagesize=A5,
                                leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
                                topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM)
        doc.build(story)
        print(f"Grimoire avec sommaire généré : {output_path}")

    def _ajouter_info(self, story, label, valeur, styles):
        if valeur:
            story.append(Paragraph(
                f"<font color='slategrey'><b>{label} :</b></font> {valeur}",
                styles["Corps"]
            ))


