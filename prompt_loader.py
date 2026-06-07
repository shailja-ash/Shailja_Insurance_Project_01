from pathlib import Path


def load_system_prompt(products):

    prompt_path = Path("prompts/insurance_system_prompt.md")

    prompt = prompt_path.read_text(
        encoding="utf-8"
    )

    prompt = prompt.replace(
        "{PRODUCTS}",
        str(products)
    )

    return prompt