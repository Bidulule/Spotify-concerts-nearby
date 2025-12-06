"""
Module main

Point d'entrée de l'application.

Ce script :
1. Charge la configuration et la base des morceaux likés.
2. Récupère les nouveaux morceaux likés depuis Spotify.
3. Analyse les artistes les plus likés.
4. Récupère les concerts à venir via l'API Setlist.fm.
5. Génère une page HTML listant les concerts en France.
"""

from src.config import load_config
from src.likes_db import load_likes_db, save_likes_db
from src.spotify_client import get_spotify_client, fetch_new_liked_tracks, count_likes_per_artist
from src.setlistfm import get_setlistfm_events
from src.html_generator import generate_html
import time

def main():
    """
    Exécute le workflow principal de l'application.

    Étapes :
        1. Charger la configuration depuis config.json.
        2. Charger les morceaux likés précédemment depuis liked_tracks.json.
        3. Créer un client Spotify authentifié.
        4. Récupérer les nouveaux morceaux likés depuis Spotify.
        5. Mettre à jour la base locale des morceaux likés.
        6. Compter les likes par artiste et demander à l'utilisateur combien d'artistes analyser.
        7. Récupérer les concerts à venir pour les artistes sélectionnés.
        8. Générer une page HTML listant les concerts.
    """
    # Chargement configuration et base de données locale
    config = load_config()
    previous_likes = load_likes_db()

    # Initialisation du client Spotify et récupération des nouveaux likes
    sp = get_spotify_client(config)
    new_likes = fetch_new_liked_tracks(sp, previous_likes)
    all_likes = {**new_likes, **previous_likes}
    save_likes_db(all_likes)

    print(f"[i] {len(new_likes)} nouveaux morceaux trouvés.")
    print(f"[i] Total de musiques likées : {len(all_likes)}")

    # Analyse des artistes
    artist_counts = count_likes_per_artist(all_likes)
    max_artists = len(artist_counts)
    default_top_n = config.get("top_artists", max_artists)

    # Demande à l'utilisateur combien d'artistes analyser
    try:
        user_input = input(f"Combien d'artistes parmi les {max_artists} veux-tu analyser ? (Entrée = {default_top_n}) : ")
        top_n = int(user_input.strip()) if user_input.strip() else default_top_n
        top_n = max(1, min(top_n, max_artists))
    except ValueError:
        print(f"[!] Entrée invalide, utilisation de la valeur par défaut : {default_top_n}")
        top_n = default_top_n

    # Tri des artistes par nombre de morceaux likés
    sorted_artists = sorted(artist_counts.items(), key=lambda x: -x[1])
    if top_n:
        sorted_artists = sorted_artists[:top_n]
        print(f"[i] Recherche des concerts pour les {top_n} artistes les plus aimés.")

    # Récupération des concerts pour chaque artiste
    artists_with_events = []
    total = len(sorted_artists)
    for i, (artist, count) in enumerate(sorted_artists, 1):
        print(f"  → ({i}/{total}) Recherche concerts de {artist}...", end="", flush=True)
        events = get_setlistfm_events(artist, config["setlistfm"]["api_key"])
        if events:
            print(f" trouvé {len(events)} date(s).")
            artists_with_events.append((artist, {"count": count, "events": events}))
        else:
            print(" aucun concert.")
        time.sleep(0.25)  # Limite les requêtes à l'API

    # Génération de la page HTML
    generate_html(artists_with_events)


if __name__ == "__main__":
    main()
