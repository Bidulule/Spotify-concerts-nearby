"""
Module likes_db

Fournit des fonctions pour gérer la base locale des morceaux likés.

Fonctions:
- save_likes_db(data): Sauvegarde les morceaux likés dans un fichier JSON.
- load_likes_db(): Charge les morceaux likés depuis le fichier JSON.
"""

import os
import json

LIKES_DB = os.path.join("outputs", "liked_tracks.json")

def save_likes_db(data):
    """
    Sauvegarde les morceaux likés dans le fichier LIKES_DB au format JSON.

    Args:
        data (dict): Dictionnaire contenant les informations des morceaux likés.

    Raises:
        IOError: Si le fichier ne peut pas être écrit.
    """
    with open(LIKES_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_likes_db():
    """
    Charge les morceaux likés depuis le fichier LIKES_DB.

    Returns:
        dict: Dictionnaire contenant les morceaux likés, vide si le fichier n'existe pas.

    Raises:
        json.JSONDecodeError: Si le fichier JSON est mal formé.
    """
    if not os.path.exists(LIKES_DB):
        return {}
    with open(LIKES_DB, encoding="utf-8") as f:
        return json.load(f)
