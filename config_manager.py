import json
import os

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
        self.config_file: str = "papier_prijzen.json"

    def load_prijzen(self)->dict[str, float]:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return DEFAULT_PRIJZEN
        except ValueError:
            return DEFAULT_PRIJZEN

    def save_prijzen(self, prijzen)->bool:
        try:
            with open(self.config_file, 'w') as f:
                json.dump(prijzen, f, indent=4)
            return True
        except ValueError:
            return False
