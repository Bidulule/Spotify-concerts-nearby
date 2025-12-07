import os
from datetime import datetime

OUTPUT_HTML = os.path.join("outputs", "concerts.html")

def generate_html(artists_data):
    """
    Génère une page HTML listant les artistes et leurs concerts.
    artists_data : dict avec deux clés :
        - "With_events": liste de tuples (artist_name, data)
        - "Without_events": liste de tuples (artist_name, data)
    Chaque `data` contient :
        - rank : int
        - count : int
        - link : str (URL Bandintown)
        - events : liste de dicts avec date, city, country, venue, url
    """
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Concerts à venir</title>
<style>
body { font-family: Arial, sans-serif; margin: 20px; }
table { border-collapse: collapse; width: 100%; margin-bottom: 40px; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th { background-color: #f2f2f2; }
a { color: #007BFF; text-decoration: none; }
a:hover { text-decoration: underline; }
.filters { margin-bottom: 20px; }
.filters label { margin-right: 10px; }
</style>
</head>
<body>

<h1>Concerts en France et ailleurs</h1>

<div class="filters">
    <label>Date début: <input type="date" id="startDate"></label>
    <label>Date fin: <input type="date" id="endDate"></label>
    <label>Pays: <input type="text" id="countryFilter" placeholder="ex: France"></label>
    <label>Ville: <input type="text" id="cityFilter" placeholder="ex: Paris"></label>
    <button onclick="applyFilters()">Filtrer</button>
    <button onclick="resetFilters()">Réinitialiser</button>
</div>

<div id="artists-container">
"""

    def artist_row(artist_name, data):
        link = data.get("link", "#")
        count = data.get("count", 0)
        rank = data.get("rank", 0)
        if count == 1:
            html_row = f'<h2><a href="{link}" target="_blank">#{rank} - {artist_name} (1 titre liké)</a></h2>\n'
        else:
            html_row = f'<h2><a href="{link}" target="_blank">#{rank} - {artist_name} ({count} titres likés)</a></h2>\n'
        events = data.get("events", [])
        if events:
            html_row += '<table class="events-table">\n<tr><th>Date</th><th>Pays</th><th>Ville</th><th>Salle</th></tr>\n'
            for e in events:
                event_date = e.get("date", "")
                venue = e.get("venue", "")
                city = e.get("city", "")
                country = e.get("country", e.get("country",""))
                url = e.get("url", "#")
                html_row += f'<tr data-date="{event_date}" data-country="{country}" data-city="{city}">' \
                            f'<td><a href="{url}" target="_blank">{event_date}</a></td>' \
                            f'<td>{country}</td><td>{city}</td><td>{venue}</td></tr>\n'
            html_row += '</table>\n'
        return html_row

    for artist, data in artists_data.get("With_events", []):
        html += artist_row(artist, data)
    for artist, data in artists_data.get("Without_events", []):
        html += artist_row(artist, data)

    html += """
</div>

<script>
function applyFilters() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const countryFilter = document.getElementById('countryFilter').value.toLowerCase();
    const cityFilter = document.getElementById('cityFilter').value.toLowerCase();
    const rows = document.querySelectorAll('.events-table tr[data-date]');
    rows.forEach(row => {
        let show = true;
        const date = row.getAttribute('data-date');
        const country = row.getAttribute('data-country').toLowerCase();
        const city = row.getAttribute('data-city').toLowerCase();
        if (startDate && new Date(date) < new Date(startDate)) show = false;
        if (endDate && new Date(date) > new Date(endDate)) show = false;
        if (countryFilter && !country.includes(countryFilter)) show = false;
        if (cityFilter && !city.includes(cityFilter)) show = false;
        row.style.display = show ? '' : 'none';
    });
}

function resetFilters() {
    document.getElementById('startDate').value = '';
    document.getElementById('endDate').value = '';
    document.getElementById('countryFilter').value = '';
    document.getElementById('cityFilter').value = '';
    document.querySelectorAll('.events-table tr[data-date]').forEach(row => row.style.display = '');
}
</script>

</body>
</html>
"""

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[✓] Page HTML générée dans {OUTPUT_HTML}")
    return OUTPUT_HTML
