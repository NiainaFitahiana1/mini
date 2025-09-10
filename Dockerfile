# Utiliser une image Python légère
FROM python:3.12-slim

# Installer dépendances système minimales
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Définir dossier de travail
WORKDIR /app

# Copier requirements
COPY requirements.txt .

# Installer dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier code
COPY . .

# Exposer le port Quart (par défaut 5000)
EXPOSE 5000

# Commande par défaut (on pourra override avec docker-compose ou docker run)
CMD ["python3", "run.py", "run"]
