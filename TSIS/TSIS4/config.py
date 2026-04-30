import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

DEFAULT_SETTINGS = {
    "snake_color": (0, 255, 0),
    "grid_overlay": False,
    "sound": True
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    with open(SETTINGS_FILE, 'r') as f:
        settings = json.load(f)
        settings['snake_color'] = tuple(settings['snake_color'])
        return settings

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

CS = 20
W, H = 30, 20
WIDTH, HEIGHT = W * CS, H * CS
