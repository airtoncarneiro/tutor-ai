"""Minimal application entrypoint for the project foundation."""

from .config import Settings


def main() -> None:
    settings = Settings()
    print(f"Adaptive SQL Tutor AI iniciado ({settings.app_env}).")


if __name__ == "__main__":
    main()
