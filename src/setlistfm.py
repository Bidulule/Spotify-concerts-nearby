"""
Module setlistfm

Fournit des fonctions pour interagir avec l'API Setlist.fm
et récupérer les événements/concerts d'artistes en France.

Fonctions:
- get_setlistfm_events(artist_name, api_key): Récupère la liste des concerts d'un artiste.
"""

import requests
import time

def get_setlistfm_events(artist_name, api_key):
    """
    Récupère les concerts à venir pour un artiste donné via l'API Setlist.fm.

    Args:
        artist_name (str): Nom de l'artiste dont on veut récupérer les concerts.
        api_key (str): Clé API Setlist.fm valide.

    Returns:
        list[dict]: Liste de dictionnaires contenant les informations sur chaque concert.
                    Chaque dictionnaire contient :
                    - "date" (str) : Date de l'événement
                    - "venue" (str) : Nom de la salle
                    - "city" (str) : Nom de la ville
                    Retourne une liste vide si aucun concert n'est trouvé ou en cas d'erreur.

    Notes:
        - La fonction filtre uniquement les concerts en France ("countryCode": "FR").
        - En cas d'erreur lors de la requête, un message est affiché et une liste vide est retournée.
    """
    url = f"https://api.setlist.fm/rest/1.0/search/setlists"
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json"
    }
    params = {
        "artistName": artist_name,
        "countryCode": "FR",
        "p": 1
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return []
        data = response.json()
        events = []
        for item in data.get("setlist", []):
            date = item.get("eventDate")
            venue = item.get("venue", {}).get("name", "")
            city = item.get("venue", {}).get("city", {}).get("name", "")
            events.append({
                "date": date,
                "venue": venue,
                "city": city
            })
        return events
    except Exception as e:
        print(f"[!] Erreur pour {artist_name} : {e}")
        return []
