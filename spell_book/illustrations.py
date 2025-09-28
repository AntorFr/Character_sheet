import os
import base64
from openai import OpenAI
from character_sheet.utils import sanitize_filename

# === PARAMÈTRES DE PROMPT ===

BASE_PROMPT = (
    "A highly detailed black-and-white ink illustration showing only the magical effect of the spell: {name}. "
    "The drawing should be in the style of an ancient necromancer’s grimoire, without any text, title, frames, runes, books, or decorative symbols. "
)

STYLISTIC_CONSTRAINTS = (
    "A highly detailed black-and-white ink illustration, some touch a color is ok. Inspired by the style of an ancient necromancer’s grimoire in world of Dungeons & Dragons"
    "Background must be fully transparent. Center the drawing with at least 15% margin around all edges to avoid clipping."
    "Ensure the drawing fades naturally into transparency at the edges, with no hard borders so it appears as if inked directly on ancient parchment.."
    "The drawing should be in the style of an ancient necromancer’s grimoire, without any text, title, frames."
)

LARGE_ILLUSTRATION_CONTEXT_PROMPT = (
    "Depict a necromantic manifestation of the spell involving diverse creatures from the Dungeons & Dragons bestiary—undead, monstrosities, fiends, or even corrupted elves, dwarves, tieflings, and orcs. "
    "The illustration should show a dramatic magical scene where necromantic energy interacts with these beings: possession, resurrection, agony, or transformation. "
    "Ensure high anatomical variety and dynamic composition, focusing on contrast, shadow, and decay to emphasize the dark magic at work."
)

PROMPT_GENERATION_INSTRUCTION = (
    "You are an expert magical illustrator. Based on the name and description of a Dungeons & Dragons spell, "
    "write a concise visual concept prompt that describes only the magical effect caused by the spell. "
    "Format your result in a single English sentence suitable for use with DALL·E."
)

class SpellIllustrationGenerator:
    def __init__(self, api_key: str, output_dir="illustrations", model="gpt-image-1", theme_style: str = None):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.output_dir = output_dir
        self.model = model
        self.theme_style = theme_style or "dark medieval necromancy, skulls, shadows, undead, gothic"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_prompt_with_chatgpt(self, spell_name: str, description: str) -> str:
        try:
            # Ajouter le style du thème aux contraintes stylistiques
            themed_constraints = f"{STYLISTIC_CONSTRAINTS} Style: {self.theme_style}"
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": PROMPT_GENERATION_INSTRUCTION },
                    {"role": "user", "content": f"""Spell name: {spell_name}
                     Description: {description}
                     Stylistic constraints: {themed_constraints}"""}
                ],
                temperature=0.7
            )
            prompt_text = response.choices[0].message.content.strip()
            print(f"🧠 Prompt généré par GPT pour '{spell_name}' (style: {self.theme_style}): {prompt_text}")
            return prompt_text
        except Exception as e:
            print(f"❌ Erreur lors de la génération du prompt pour '{spell_name}': {e}")
            return BASE_PROMPT.format(name=spell_name)

    def generate_illustration(self, spell_name: str, description: str) -> str:
        filename = sanitize_filename(spell_name) + ".png"
        filepath = os.path.join(self.output_dir, filename)

        if os.path.exists(filepath):
            print(f"✔ Illustration déjà générée pour '{spell_name}', chargée depuis {filepath}")
            return filepath

        # Combiner les contraintes stylistiques avec le style du thème
        themed_prompt = f"{STYLISTIC_CONSTRAINTS} Style: {self.theme_style}. " + self.generate_prompt_with_chatgpt(spell_name, description)

        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=themed_prompt,
                n=1,
                size="1024x1024",
                output_format="png",
                quality="low"
            )

            image_base64 = response.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)

            # Save the image to a file
            with open(filepath, "wb") as f:
                f.write(image_bytes)

            print(f"✅ Illustration générée et enregistrée : {filepath}")
            return filepath

        except Exception as e:
            print(f"❌ Erreur lors de la génération de l'illustration pour '{spell_name}': {e}")
            return None

    def generate_large_illustration(self, spell_name: str, description: str, prompt_addition: str = "") -> str:
        large_dir = os.path.join(self.output_dir, "large")
        os.makedirs(large_dir, exist_ok=True)

        filename = sanitize_filename(spell_name) + ".png"
        filepath = os.path.join(large_dir, filename)

        if os.path.exists(filepath):
            print(f"✔ Illustration large déjà générée pour '{spell_name}', chargée depuis {filepath}")
            return filepath

        base_prompt = self.generate_prompt_with_chatgpt(spell_name, description)
        final_prompt = (
            f"{STYLISTIC_CONSTRAINTS} Style: {self.theme_style}. " +
            LARGE_ILLUSTRATION_CONTEXT_PROMPT + " " +
            base_prompt + " " +
            prompt_addition
        )

        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=final_prompt.strip(),
                n=1,
                size="1024x1536", 
                output_format="png",
                quality="medium"
            )

            image_base64 = response.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)

            with open(filepath, "wb") as f:
                f.write(image_bytes)

            print(f"✅ Illustration A5 large générée et enregistrée : {filepath}")
            return filepath

        except Exception as e:
            print(f"❌ Erreur lors de la génération de l'illustration large pour '{spell_name}': {e}")
            return None
