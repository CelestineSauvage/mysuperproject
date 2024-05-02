# Utilisation de Python
FROM python:3.12-slim

# Copie du fichier de requirements
COPY src/data_consumption/requirements.txt ./requirements.txt

# Installation des dépendances Python
RUN pip3 install -r requirements.txt

# Copie des autres fichiers dans le conteneur
COPY src/data_consumption ./

# Exposition du port 80 pour l'application
ENV MONGO_HOST localhost
EXPOSE 80

# Commande par défaut à exécuter lorsque le conteneur démarre
CMD ["python3", "data_consumer.py"]