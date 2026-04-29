import json
import os

SETTINGS_FILE = 'settings.json'
LEADERBOARD_FILE = 'leaderboard.json'

DEFAULT_SETTINGS = {
    "sound": True,
    "color": "blue",
    "difficulty": "normal"
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)

def save_settings(settings_data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings_data, f, indent=4)

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, 'r') as f:
        return json.load(f)

def save_score(name, score, distance):
    board = load_leaderboard()
    board.append({"name": name, "score": score, "distance": distance})
    board = sorted(board, key=lambda x: x["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(board, f, indent=4)
