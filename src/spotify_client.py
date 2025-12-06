"""
Module spotify_client

Fournit des fonctions pour interagir avec l'API Spotify et analyser les morceaux likés.

Fonctions:
- get_spotify_client(config): Crée et retourne un client Spotify authentifié.
- fetch_new_liked_tracks(sp, previous_likes): Récupère les nouveaux morceaux likés par l'utilisateur.
- count_likes_per_artist(all_likes): Compte le nombre de likes par artiste.
"""

import time
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

def get_spotify_client(config):
    """
    Crée un client Spotify authentifié à partir de la configuration.

    Args:
        config (dict): Dictionnaire contenant les clés 'client_id', 'client_secret', et 'redirect_uri' sous 'spotify'.

    Returns:
        Spotify: Instance du client Spotify authentifié.

    Raises:
        spotipy.SpotifyException: Si l'authentification échoue.
    """
    return Spotify(auth_manager=SpotifyOAuth(
        client_id=config["spotify"]["client_id"],
        client_secret=config["spotify"]["client_secret"],
        redirect_uri=config["spotify"]["redirect_uri"],
        scope="user-library-read"
    ))

def fetch_new_liked_tracks(sp, previous_likes):
    """
    Récupère les morceaux récemment likés par l'utilisateur Spotify.

    Args:
        sp (Spotify): Client Spotify authentifié.
        previous_likes (dict): Dictionnaire des morceaux déjà likés {track_id: info}.

    Returns:
        dict: Nouveau dictionnaire des morceaux likés depuis le dernier fetch.

    Notes:
        La fonction s'arrête lorsqu'elle rencontre un morceau déjà existant dans previous_likes.
        Utilise des pauses pour limiter le nombre de requêtes à l'API.
    """
    new_likes = {}
    seen = set(previous_likes)
    offset = 0
    while True:
        results = sp.current_user_saved_tracks(limit=50, offset=offset)
        if not results["items"]:
            break
        for item in results["items"]:
            track = item["track"]
            if track["id"] in seen:
                return new_likes
            artist_names = [artist["name"] for artist in track["artists"]]
            new_likes[track["id"]] = {
                "name": track["name"],
                "artists": artist_names
            }
        offset += 50
        time.sleep(0.2)
    return new_likes

def count_likes_per_artist(all_likes):
    """
    Compte le nombre de morceaux likés par chaque artiste.

    Args:
        all_likes (dict): Dictionnaire de morceaux likés {track_id: {"name": str, "artists": [str]}}.

    Returns:
        dict: Dictionnaire trié par nombre de morceaux likés par artiste, ordre décroissant.
              Format: {artist_name: count}
    """
    from collections import defaultdict
    counter = defaultdict(int)
    for track in all_likes.values():
        for artist in track["artists"]:
            counter[artist] += 1
    return dict(sorted(counter.items(), key=lambda x: -x[1]))
