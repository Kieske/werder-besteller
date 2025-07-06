import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_deadlines():
    url = "https://www.werder.de/tickets/heimspiele/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    deadlines = {}

    # Beispiel: Suche nach dem Bereich mit den Fristen (je nach Webseite anpassen)
    fristen_section = soup.find('section', id='bestellfristen')  # Beispiel-ID, prüfen!
    if not fristen_section:
        print("Fristen-Bereich nicht gefunden")
        return deadlines

    # Beispiel: Alle Fristen in Listenpunkten auslesen
    for li in fristen_section.find_all('li'):
        text = li.get_text(strip=True)
        # Beispiel: "Spiel gegen XYZ – Bestellfrist: 15.08.2025"
        if "Bestellfrist:" in text:
            parts = text.split("–")
            if len(parts) >= 2:
                game = parts[0].replace("Spiel gegen ", "").strip()
                date_str = parts[1].replace("Bestellfrist:", "").strip()
                try:
                    deadline_date = datetime.strptime(date_str, "%d.%m.%Y").date()
                    deadlines[game] = deadline_date
                except ValueError:
                    print(f"Datum konnte nicht geparst werden: {date_str}")

    return deadlines
