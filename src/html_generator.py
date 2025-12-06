"""
Module html_generator

Fournit une fonction pour générer une page HTML listant les concerts
à venir pour les artistes likés par l'utilisateur.

Fonctions:
- generate_html(artists_data): Génère un fichier HTML avec les concerts.
"""

import os

OUTPUT_HTML = os.path.join("outputs", "concerts.html")

def generate_html(artists_data):
    """
    Génère une page HTML listant les concerts à venir pour chaque artiste.

    Args:
        artists_data (list[tuple]): Liste de tuples (artist_name, data) où :
            - artist_name (str) : Nom de l'artiste.
            - data (dict) : Contient :
                - "count" (int) : Nombre de morceaux likés.
                - "events" (list[dict]) : Liste des concerts, chaque dict contient :
                    - "date" (str) : Date du concert
                    - "venue" (str) : Nom de la salle
                    - "city" (str) : Ville

    Returns:
        None: Écrit le fichier HTML dans OUTPUT_HTML.

    Notes:
        - Si un artiste n'a aucun événement, il est ignoré.
        - Le fichier est écriture en UTF-8.
        - Affiche un message de confirmation à la fin.
    """
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
