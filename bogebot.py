import requests
from bs4 import BeautifulSoup
import time
import os
import threading
from flask import Flask, render_template_string

# Configurations
URL = "https://www.laboge.fr/bons-plans?title=asse&field_lieu_value=asse&category=27&field_begin_date_value=All"
HEADERS = {"User-Agent": "Mozilla/5.0"}
NTFY_URL = "https://bogentfy.onrender.com/asse-places"
SEEN_OFFERS = set()
logs = []

# Web app
app = Flask(__name__)

@app.route("/")
def show_logs():
    return render_template_string("<pre>{{ logs }}</pre>", logs="\n".join(logs[-100:]))

def check_offers():
    try:
        response = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        offres = soup.select("li > a.teaser__bg")
        if not offres:
            logs.append("Aucune offre trouvée.")
            return None

        new_offers = []

        for offre in offres:
            titre_elem = offre.select_one("p.teaser__title")
            places_elem = offre.select_one("span.teaser__slots")
            lien = offre.get("href", "")
            lien_complet = "https://www.laboge.fr" + lien
            titre = titre_elem.text.strip() if titre_elem else "Titre inconnu"
            places = places_elem.text.strip() if places_elem else "Places inconnues"
            offer_id = f"{titre}|{places}|{lien_complet}"
            if offer_id not in SEEN_OFFERS:
                SEEN_OFFERS.add(offer_id)
                new_offers.append({
                    "titre": titre,
                    "places": places,
                    "lien": lien_complet
                })

        return new_offers if new_offers else None
    except Exception as e:
        logs.append(f"Erreur lors du scraping : {e}")
        return None

def send_notification(message):
    headers = {
        "Title": "Nouvelle offre ASSE",
        "Priority": "urgent",
        "Tags": "ticket"
    }
    try:
        response = requests.post(NTFY_URL, data=message, headers=headers)
        if response.status_code == 200:
            logs.append(f"✅ Notification envoyée : {message}")
        else:
            logs.append(f"❌ Erreur notification ({response.status_code}) : {message}")
    except Exception as e:
        logs.append(f"❌ Exception en envoyant notification : {e}")

def main_loop():
    while True:
        logs.append("🔄 Vérification des offres...")
        new_offers = check_offers()

        if new_offers:
            logs.append(f"🆕 {len(new_offers)} nouvelles offres détectées.")
            for offer in new_offers:
                message = f"{offer['titre']} ({offer['places']}) → {offer['lien']}"
                send_notification(message)
        time.sleep(30)

if __name__ == "__main__":
    threading.Thread(target=main_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)

