import time
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

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
    from collections import defaultdict
    counter = defaultdict(int)
    for track in all_likes.values():
        for artist in track["artists"]:
            counter[artist] += 1
    return dict(sorted(counter.items(), key=lambda x: -x[1]))
