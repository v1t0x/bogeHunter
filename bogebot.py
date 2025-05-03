import requests
from bs4 import BeautifulSoup
import time
import os

# URL et autres paramètres
URL = "https://www.laboge.fr/bons-plans?title=asse&field_lieu_value=asse&category=27&field_begin_date_value=All"
HEADERS = {"User-Agent": "Mozilla/5.0"}
NTFY_URL = "https://bogentfy.onrender.com/asse-places"  # URL de ntfy

# Ensemble global pour stocker les offres déjà vues
SEEN_OFFERS = set()

# Fonction pour récupérer les offres et envoyer une notification
def check_offers():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    offres = soup.select("li > a.teaser__bg")

    if not offres:
        print("Aucune offre trouvée.")
        return None

    # On récupère le titre et le nombre de places pour chaque offre
    all_offers = []
    new_offers = []
    
    for offre in offres:
        titre_elem = offre.select_one("p.teaser__title")
        places_elem = offre.select_one("span.teaser__slots")
        lien = offre.get("href", "")
        lien_complet = "https://www.laboge.fr" + lien

        titre = titre_elem.text.strip() if titre_elem else "Titre inconnu"
        places = places_elem.text.strip() if places_elem else "Places inconnues"

        # Créer un identifiant unique pour cette offre
        offer_id = f"{titre}|{places}|{lien_complet}"
        offer_data = {"titre": titre, "places": places, "lien": lien_complet}
        
        all_offers.append(offer_data)
        
        # Vérifier si c'est une nouvelle offre
        if offer_id not in SEEN_OFFERS:
            SEEN_OFFERS.add(offer_id)
            new_offers.append(offer_data)

    # Retourner uniquement les nouvelles offres
    return new_offers if new_offers else None

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
    while True:
        print("Vérification des offres...")
        new_offers = check_offers()

        if new_offers:
            print(f"{len(new_offers)} nouvelles offres détectées.")
            for offer in new_offers:
                message = f" {offer['titre']} ({offer['places']}) → {offer['lien']}"
                send_notification(message)

        # Attendre 5 minutes avant la prochaine vérification
        time.sleep(30)

if __name__ == "__main__":
    main()
