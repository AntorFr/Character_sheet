import os
import base64
from openai import OpenAI
from character_sheet.utils import sanitize_filename
from .theme_manager import ThemeManager

PROMPT_GENERATION_INSTRUCTION = (
    "You are an expert magical illustrator. Based on the name and description of a Dungeons & Dragons spell, "
    "write a concise visual concept prompt that describes only the magical effect caused by the spell. "
    "Format your result in a single English sentence suitable for use with DALL·E."
)

class SpellIllustrationGenerator:
    def __init__(self, api_key: str, output_dir="illustrations", model="gpt-image-1", theme_manager: ThemeManager = None):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.output_dir = output_dir
        self.model = model
        self.theme_manager = theme_manager
        self.theme_style = theme_manager.get_illustration_style() if theme_manager else "fantasy art"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_prompt_with_chatgpt(self, spell_name: str, description: str) -> str:
        try:
            # Utiliser les contraintes stylistiques du thème
            stylistic_constraints = self.theme_manager.get_stylistic_constraints() if self.theme_manager else "A detailed fantasy illustration"
            themed_constraints = f"{stylistic_constraints} Style: {self.theme_style}"
            
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
            base_prompt = self.theme_manager.get_base_prompt() if self.theme_manager else "A detailed illustration of the spell: {name}"
            return base_prompt.format(name=spell_name)

    def generate_illustration(self, spell_name: str, description: str) -> str:
        filename = sanitize_filename(spell_name) + ".png"
        filepath = os.path.join(self.output_dir, filename)

        if os.path.exists(filepath):
            print(f"✔ Illustration déjà générée pour '{spell_name}', chargée depuis {filepath}")
            return filepath

        # Combiner les contraintes stylistiques du thème avec le style
        stylistic_constraints = self.theme_manager.get_stylistic_constraints() if self.theme_manager else "A detailed fantasy illustration"
        themed_prompt = f"{stylistic_constraints} Style: {self.theme_style}. " + self.generate_prompt_with_chatgpt(spell_name, description)

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
        stylistic_constraints = self.theme_manager.get_stylistic_constraints() if self.theme_manager else "A detailed fantasy illustration"
        large_context = self.theme_manager.get_large_illustration_context() if self.theme_manager else ""
        final_prompt = (
            f"{stylistic_constraints} Style: {self.theme_style}. " +
            large_context + " " +
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
