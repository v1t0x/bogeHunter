# Utilise une image Python légère
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le script dans le conteneur
COPY bogebot.py .

# Installer les dépendances nécessaires
RUN pip install --no-cache-dir requests beautifulsoup4


# Commande pour exécuter le script
CMD ["python", "bogebot.py"]

