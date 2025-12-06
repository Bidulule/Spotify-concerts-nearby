"""
Module config

Fournit des fonctions pour gérer la configuration du projet.

Fonctions:
- load_config(): Charge le fichier de configuration JSON.
"""

import json

CONFIG_PATH = "config.json"

def load_config():
    """
    Charge la configuration depuis le fichier JSON défini par CONFIG_PATH.

    Returns:
        dict: Dictionnaire contenant les paramètres de configuration.
    
    Raises:
        FileNotFoundError: Si le fichier CONFIG_PATH n'existe pas.
        json.JSONDecodeError: Si le fichier JSON est mal formé.
    """
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)
