import requests
import time

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
