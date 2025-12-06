import os

OUTPUT_HTML = os.path.join("outputs", "concerts.html")

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
