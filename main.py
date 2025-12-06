from src.config import load_config
from src.likes_db import load_likes_db, save_likes_db
from src.spotify_client import get_spotify_client, fetch_new_liked_tracks, count_likes_per_artist
from src.setlistfm import get_setlistfm_events
from src.html_generator import generate_html
import time

def main():
    config = load_config()
    previous_likes = load_likes_db()
    sp = get_spotify_client(config)
    new_likes = fetch_new_liked_tracks(sp, previous_likes)
    all_likes = {**new_likes, **previous_likes}
    save_likes_db(all_likes)

    print(f"[i] {len(new_likes)} nouveaux morceaux trouvés.")
    print(f"[i] Total de musiques likées : {len(all_likes)}")

    artist_counts = count_likes_per_artist(all_likes)
    max_artists = len(artist_counts)
    default_top_n = config.get("top_artists", max_artists)
    try:
        user_input = input(f"Combien d'artistes parmi les {max_artists} veux-tu analyser ? (Entrée = {default_top_n}) : ")
        top_n = int(user_input.strip()) if user_input.strip() else default_top_n
        top_n = max(1, min(top_n, max_artists))
    except ValueError:
        print(f"[!] Entrée invalide, utilisation de la valeur par défaut : {default_top_n}")
        top_n = default_top_n
    sorted_artists = sorted(artist_counts.items(), key=lambda x: -x[1])
    if top_n:
        sorted_artists = sorted_artists[:top_n]
        print(f"[i] Recherche des concerts pour les {top_n} artistes les plus aimés.")

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
        time.sleep(0.25)

    generate_html(artists_with_events)

if __name__ == "__main__":
    main()
