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
    "A highly detailed black-and-white ink illustration, inspired by the style of an ancient necromancer’s grimoire in world of Dungeons & Dragons"
    "Background must be fully transparent. Center the drawing with at least 15% margin around all edges to avoid clipping." 
    "Ensure the drawing fades naturally into transparency at the edges, with no hard borders."
)

PROMPT_GENERATION_INSTRUCTION = (
    "You are an expert magical illustrator. Based on the name and description of a Dungeons & Dragons spell, "
    "write a concise visual concept prompt that describes only the magical effect caused by the spell. "
    "Format your result in a single English sentence suitable for use with DALL·E."
)

class SpellIllustrationGenerator:
    def __init__(self, api_key: str, output_dir="illustrations", model="gpt-image-1"):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.output_dir = output_dir
        self.model = model
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_prompt_with_chatgpt(self, spell_name: str, description: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": PROMPT_GENERATION_INSTRUCTION },
                    {"role": "user", "content": f"""Spell name: {spell_name}
                     Description: {description}
                     Stylistic constraints: {STYLISTIC_CONSTRAINTS}"""}
                ],
                temperature=0.7
            )
            prompt_text = response.choices[0].message.content.strip()
            print(f"🧠 Prompt généré par GPT pour '{spell_name}': {prompt_text}")
            return prompt_text
        except Exception as e:
            print(f"❌ Erreur lors de la génération du prompt pour '{spell_name}': {e}")
            return BASE_PROMPT.format(name=spell_name)
        except Exception as e:
            print(f"❌ Erreur lors de la génération du prompt pour '{spell_name}': {e}")
            return BASE_PROMPT.format(name=spell_name)

    def generate_illustration(self, spell_name: str, description: str) -> str:
        filename = sanitize_filename(spell_name) + ".png"
        filepath = os.path.join(self.output_dir, filename)

        if os.path.exists(filepath):
            print(f"✔ Illustration déjà générée pour '{spell_name}', chargée depuis {filepath}")
            return filepath

        prompt = STYLISTIC_CONSTRAINTS + "" +  self.generate_prompt_with_chatgpt(spell_name, description)

        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
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
