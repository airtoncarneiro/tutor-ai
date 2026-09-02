from pathlib import Path


def load_prompt(path: Path | str = "prompts/adaptive_sql_tutor.md") -> str:
    prompt_path = Path(path)
    if not prompt_path.is_file():
        raise FileNotFoundError(f"Prompt não encontrado: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")

