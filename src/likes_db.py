import os
import json

LIKES_DB = os.path.join("outputs", "liked_tracks.json")

def save_likes_db(data):
    with open(LIKES_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_likes_db():
    if not os.path.exists(LIKES_DB):
        return {}
    with open(LIKES_DB, encoding="utf-8") as f:
        return json.load(f)
