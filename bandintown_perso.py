import json
import os
import requests
import time
from collections import defaultdict
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

CONFIG_PATH = "config.json"
LIKES_DB = "liked_tracks.json"
OUTPUT_HTML = "concerts.html"

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def save_likes_db(data):
    with open(LIKES_DB, "w") as f:
        json.dump(data, f, indent=2)

def load_likes_db():
    if not os.path.exists(LIKES_DB):
        return {}
    with open(LIKES_DB) as f:
        return json.load(f)

def get_spotify_client(config):
    return Spotify(auth_manager=SpotifyOAuth(
        client_id=config["spotify"]["client_id"],
        client_secret=config["spotify"]["client_secret"],
        redirect_uri=config["spotify"]["redirect_uri"],
        scope="user-library-read"
    ))

def fetch_new_liked_tracks(sp, previous_likes):
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
    counter = defaultdict(int)
    for track in all_likes.values():
        for artist in track["artists"]:
            counter[artist] += 1
    return dict(sorted(counter.items(), key=lambda x: -x[1]))

def get_setlistfm_events(artist_name, api_key):
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

def generate_html(artists_data):
    html = """<html><head><meta charset="utf-8"><title>Concerts à venir</title></head><body>
    <h1>Concerts en France</h1>"""
    for artist, data in artists_data:
        if not data["events"]:
            continue
        html += f"<h2>{artist} ({data['count']} titre(s) liké(s))</h2><ul>"
        for event in data["events"]:
            html += f"<li>{event['date']} – {event['venue']} ({event['city']})</li>"
        html += "</ul>"
    html += "</body></html>"
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n[✓] Page HTML générée dans {OUTPUT_HTML}")

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
    print(f"[i] Total artistes likés : {len(artist_counts)}")
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
            artists_with_events.append((artist, {
                "count": count,
                "events": events
            }))
        else:
            print(" aucun concert.")
        time.sleep(0.25)

    generate_html(artists_with_events)

if __name__ == "__main__":
    main()
