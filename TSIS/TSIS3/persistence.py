import json
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE    = os.path.join(_DIR, "settings.json")
LEADERBOARD_FILE = os.path.join(_DIR, "leaderboard.json")

DEFAULT_SETTINGS = {
    "sound":      False,
    "car_color":  [50, 100, 220],
    "difficulty": "normal"
}


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        for k, v in DEFAULT_SETTINGS.items():
            data.setdefault(k, v)
        return data
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE) as f:
            return json.load(f)
    return []


def save_leaderboard(entries):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def add_score(username, score, distance, coins):
    entries = load_leaderboard()
    entries.append({
        "username": username,
        "score":    score,
        "distance": distance,
        "coins":    coins,
    })
    entries.sort(key=lambda x: x["score"], reverse=True)
    entries = entries[:10]
    save_leaderboard(entries)
