import requests
from bs4 import BeautifulSoup
import time
import os

# URL et autres paramètres
URL = "https://www.laboge.fr/bons-plans?title=asse&field_lieu_value=asse&category=27&field_begin_date_value=All"
HEADERS = {"User-Agent": "Mozilla/5.0"}
NTFY_URL = "https://bogentfy.onrender.com/asse-places"  # URL de ntfy

# Fonction pour récupérer les offres et envoyer une notification
def check_offers():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    offres = soup.select("li > a.teaser__bg")

    if not offres:
        print("Aucune offre trouvée.")
        return None

    # On récupère le titre et le nombre de places pour chaque offre
    offers = []
    for offre in offres:
        titre_elem = offre.select_one("p.teaser__title")
        places_elem = offre.select_one("span.teaser__slots")
        lien = offre.get("href", "")
        lien_complet = "https://www.laboge.fr" + lien

        titre = titre_elem.text.strip() if titre_elem else "Titre inconnu"
        places = places_elem.text.strip() if places_elem else "Places inconnues"

        offers.append({"titre": titre, "places": places, "lien": lien_complet})

    return offers

# Fonction pour envoyer une notification via NTFY
def send_notification(message):
    headers = {
        "Title": "Nouvelle offre ASSE",
        "Priority": "urgent",
        "Tags": "ticket"  # ou "test", ou ce que tu veux
    }
    response = requests.post(NTFY_URL, data=message, headers=headers)
    if response.status_code == 200:
        print(f"Notification envoyée : {message}")
    else:
        print(f"Erreur en envoyant la notification : {response.status_code}")

# Fonction principale
def main():
    last_offer = None
    while True:
        print("Vérification des offres...")
        current_offers = check_offers()

        if current_offers and current_offers != last_offer:
            print("Nouvelles offres détectées.")
            for offer in current_offers:
                message = f" {offer['titre']} ({offer['places']}) → {offer['lien']}"
                send_notification(message)
            last_offer = current_offers

        # Attendre 5 minutes avant la prochaine vérification
        time.sleep(300)

if __name__ == "__main__":
    main()

