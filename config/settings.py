# config/settings.py
import json
import os

DEFAULT_SETTINGS = {
    "auto_nexus_percent": 30,
    "movement_mode": "Kiting",
    "player_class": "Wizard",
    "keybinds": {
        "move_up": "w",
        "move_down": "s",
        "move_left": "a",
        "move_right": "d",
        "attack": "left",
        "nexus": "r",
        "drop_item": None
    }
}

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'user_config.json')

def load_config():
    # Load config from JSON file, or return defaults
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
        return {**DEFAULT_SETTINGS, **data}
    return DEFAULT_SETTINGS.copy()

def save_config(config):
    # Write config back to JSON
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

