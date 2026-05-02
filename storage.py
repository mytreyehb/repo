import json
import os

FILE = "players.json"

def load_players():
    if os.path.exists(FILE):
        return json.load(open(FILE))
    return {}

def save_players(players):
    json.dump(players, open(FILE, "w"))