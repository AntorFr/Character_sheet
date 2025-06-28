import os
import json
from time import sleep
from openai import OpenAI
from character_sheet.utils import sanitize_filename

class SpellSheetGenerator:
    def __init__(self, api_key: str, output_dir: str = "fiches_sorts"):
        self.api_key = api_key
        self.output_dir = output_dir
        self.client = OpenAI(api_key=self.api_key)
        os.makedirs(self.output_dir, exist_ok=True)
        self.index_path = os.path.join(self.output_dir, "index.json")
        self.index_data = self._load_index()

    def _load_index(self):
        if os.path.exists(self.index_path):
            with open(self.index_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_index(self):
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(self.index_data, f, indent=4, ensure_ascii=False)

    def _create_prompt(self, spell_name: str) -> str:
        return f"""
Tu es un expert de Donjons & Dragons 5e (règles officielles de l'édition 2014).

Donne-moi la fiche complète du sort "{spell_name}" en français, sous forme d’un **objet JSON** strictement conforme, avec les champs suivants :

- "Nom" (en français)
- "Nom original" (en anglais, tel qu’indiqué dans les sources officielles)
- "Niveau" (entier entre 0 et 9 ; 0 si c’est un tour de magie)
- "École"
- "Temps d'incantation"
- "Portée" (en **mètres**, pas en pieds. Convertis précisément. Par exemple : 30 feet → 9 mètres.)
- "Cible" (description de la ou des cibles principales du sort)
- "Composantes"
- "Durée"
- "Concentration" (true si le sort nécessite de la concentration, false sinon)
- "Rituel" (oui ou non)
- "Temps du rituel" (si applicable, sinon null)
- "Type d'attaque / sauvegarde"
- "Effet synthétique" (résumé en 1-2 phrases)
- "Description complète"
- "Effet en surcaste" (si applicable, sinon null)

Les données doivent être exactes selon les règles officielles de D&D 5e (édition 2014). Utilise comme référence :
- https://www.aidedd.org/dnd-filters/spells-5e.php
- https://dnd5e.wikidot.com/

⚠️ Important : toutes les distances et zones doivent être données **en mètres**. Utilise une conversion réaliste (1 pied = 0,3 mètre), avec arrondis raisonnables (ex: 10 pieds → 3 m, 30 pieds → 9 m, 60 pieds → 18 m, 120 pieds → 36 m).

Fournis uniquement du JSON sans texte explicatif autour.
"""

    def generate_spell_file(self, spell_name: str):
        filename = f"{sanitize_filename(spell_name)}.json"
        filepath = os.path.join(self.output_dir, filename)

        if os.path.exists(filepath):
            print(f"⏭️  Sort déjà généré : {filename} — ignoré.")
            return

        print(f"📤 Génération du sort : {spell_name}")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": self._create_prompt(spell_name)}],
                temperature=0.5,
            )
            content = response.choices[0].message.content

            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                print(f"⚠️ Erreur de parsing JSON pour {spell_name}, sauvegarde brute.")
                data = {"erreur": "JSON non valide", "contenu_brut": content}

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            # Mise à jour de l’index (si pas en erreur)
            if "Nom" in data and "Nom original" in data and "Niveau" in data:
                self.index_data.append({
                    "Nom": data["Nom"],
                    "Nom original": data["Nom original"],
                    "Niveau": data["Niveau"],
                    "Fichier": filename
                })
                self._save_index()

            sleep(1)  # Respect API

        except Exception as e:
            print(f"❌ Erreur pour le sort {spell_name} : {e}")

    def generate_spell_files(self, spell_list: list[str]):
        for spell in spell_list:
            self.generate_spell_file(spell)
