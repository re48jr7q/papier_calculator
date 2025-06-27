__version__ = "0.1.1"

import json
from pathlib import Path

DEFAULT_PRIJZEN = {
    "preprint 80": 0.0150,
    "preprint 90": 0.0120,
    "preprint 100": 0.0170,
    "preprint 120": 0.0160,
    "preprint 350": 0.0320,
    "greentop 90": 0.0110,
    "silk 300": 0.0300,
    "silk 400": 0.0380,
    "HVO 80": 0.0090,
    "biotop 90": 0.0150,
    "biotop 100": 0.0210,
    "biotop 120": 0.0240,
    "biotop 300": 0.0280,
}


class ConfigManager:
    def __init__(self):
        self.config_file = Path("../../papier_prijzen.json").resolve()

    def load_prijzen(self) -> dict[str, float]:
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {str(k): float(v) for k, v in data.items()}
            return DEFAULT_PRIJZEN
        except (ValueError, json.JSONDecodeError, OSError):
            return DEFAULT_PRIJZEN

    def save_prijzen(self, prijzen: dict) -> bool:

        try:
            # Maak backup van bestaand bestand
            if self.config_file.exists():
                backup_file = self.config_file.with_suffix('.json.bak')
                self.config_file.rename(backup_file)

            # Schrijf nieuwe data
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(prijzen, f, indent=4)
            return True
        except (OSError, TypeError, ValueError):
            # Herstel backup bij fout
            if 'backup_file' in locals():
                backup_file.rename(self.config_file)
            return False

