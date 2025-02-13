# Projet Python sur le projet fil rouge 'Job Market'

## Contexte
Ce projet fil-rouge en équipe intervient pour la session bootcamp février 2024 pour la formation Data Engineer.
Il a pour but de mettre en avant nos compétences de Data Engineer acquises durant la formation.
Pour cela ici l'idée est de regrouper des informations sur les offres d’emplois et les compagnies qui les proposent, afin d'avoir connaissance par exemple des secteurs les plus recruteurs, des compétences requises, des villes les plus actives, etc…
Le sujet détaillé se retrouve [ici](https://docs.google.com/document/d/1qnaWpbtLlFnA8nhIDxVVE8HBoDjdrAvb0slaYhZHkEY/edit?usp=drive_web&ouid=110530579869330944922)

## Auteurs
- Célestine SAUVAGE
- Emmanuelle LASTRUCCI
- Fabien WAY

## PREREQUIS PYTHON 3
Il vous faut Python en version 3.12.0

## REMARQUES
Les informations ci-dessous sont amenées à changer au fil du projet.

## MISE EN PLACE DU PROJET

- Cloner le dépôt Git :
```shell script
git clone git@github.com:YOUR_GIT_USERNAME/FEV24-BDE-JOBMARKET.git
```

- Ouvrir la copie locale :
```shell script
cd FEV24-BDE-JOBMARKET
```

- Installer venv si pas déjà installé :
```shell script
sudo apt-get install python3.12-venv
```

- Créer un environnement virtuel :
```shell script
python3.12 -m venv .penv 
```

- Activer l'environnement virtuel :
```shell script
source .penv/bin/activate
```

- Installer les paquettages Python à l'aide de pip3 :
```shell script
pip3 install -r requirements.txt
```

- Installer le navigateur Web Google Chrome nécessaire pour le paquettage Selenium :
```shell script
sudo apt install google-chrome-stable
```
```shell script
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
```
```shell script
sudo dpkg -i google-chrome-stable_current_amd64.deb
```
```shell script
sudo apt -f install
```

- Vérifier que le navigateur Web Google Chrome est bien installé :
```shell script
google-chrome --version
```

## LANCEMENT DE LA RECUPERATION DES DONNEES
```bash
python3 src/data_download.py  --path downloads/FT --source 0 --department 75  --publieeDepuis 1
python3 src/data_download.py --path downloads/APEC --source 1  --publieeDepuis jour
```

## PROCESSING DES FICHIERS
```bash
python3 src/data_transform.py --path downloads/FT --source 0  
python3 src/data_transform.py --path downloads/APEC --source 1
```

## LOAD DANS LA BDD
```bash
python3 src/load_data_into_db.py --path downloads/FT
python3 src/load_data_into_db.py --path downloads/APEC
```


## VARIABLES D'ENVIRONNEMENT
Pour lancer le projet directement, il est nécessaire de définir 4 variables globales dans votre `.bashrc`.
```bash
# CLEF FRANCE TRAVAIL A RECUPERER ICI : https://francetravail.io/
export FRANCE_EMPLOI_CLIENT_ID= #CLEF CLIENT
export FRANCE_EMPLOI_CLIENT_SECRET= #CLEF SECRET

# ADMIN MONGODO
export MONGO_ADMIN=admin #valeur par défaut 
export MONGO_ADMIN_PASS=pass #valeur par défaut 


## CREATION ET LANCEMENT DE LA PILLE DOCKER (INCLUANT LE SYSTEME DE GESTION DE BDD NOSQL MONGODB)
- Start mongodb and mongo-express contrainer
```shell script
sudo docker-compose up -d
```

## LANCEMENT DE FAST-API
### EN LIGNE DE COMMANDE (pour dev uniquement)
(Se positionner au préalable dans le dossier `src` du projet)
 - Accès en local 
```shell script
uvicorn api.MongoDBAPI:app --port 8000 --reload
```
- Accès depuis l'extérieur 
```shell script
uvicorn api.MongoDBAPI:app --host 0.0.0.0 --port 8000 --reload
```

### VIA DOCKER
(Se positionner au préalable à la racine du projet)
Créer l'image
```shell script
docker build --no-cache -t jmfastapi:1.0.0 -f src/api/Dockerfile .
```
Créer et lancer un nouveau container à partir de l'image créée
```shell script
docker run --network host -it jmfastapi:1.0.0
```

## LANCEMENT DE DASH
### EN LIGNE DE COMMANDE (pour dev uniquement)
 - Accès depuis l'extérieur (par défaut car l'host 0.0.0.0 est paramétré dans le code)
```shell script
python3 src/data_consumption/data_consumer.py
```

### VIA DOCKER
(Se positionner au préalable à la racine du projet)
Créer l'image
```shell script
docker build --no-cache -t jmdash:1.0.0 -f src/data_consumption/Dockerfile .
```
Créer et lancer un nouveau container à partir de l'image créée
```shell script
docker run --network host -it jmdash:1.0.0



## LANCEMENT DE FAST-API
pour le développement (se mettre dans le dossier `src`):
 - Accès en local 
```shell script
uvicorn api.MongoDBAPI:app --port 8000 --reload
```
- Accès depuis l'extérieur 
```shell script
uvicorn api.MongoDBAPI:app --host 0.0.0.0 --port 8000 --reload
```

##### VARIABLE NECERSSAIRE DANS .env pour le fonctionnement du projet
PROJECT_DIR=

DOWNLOAD_DIR_FT=$PROJECT_DIR/download/FT
DOWNLOAD_DIR_APEC=$PROJECT_DIR/download/APEC



## CREATION DES IMAGES
sudo docker image build -t etl_extract:1.0.0 -f src/extract/Dockerfile .
sudo docker image build -t etl_transform:1.0.0 -f src/transform/Dockerfile .
sudo docker image build -t etl_load_into_db:1.0.0 -f src/load/Dockerfile .

## Création des volumes de partages sur le host
mkdir -p /home/lastrucci/Téléchargements/TEST_PROJECT/logs_from_airflow
<!-- mkdir -p "/home/lastrucci/Téléchargements/TEST_PROJECT/downloads_from_airflow/FT"
mkdir -p "/home/lastrucci/Téléchargements/TEST_PROJECT/downloads_from_airflow/APEC" -->


# Initiate airflow db:


echo -e "AIRFLOW_UID=$(id -u)" >> .env
echo -e "AIRFLOW_GID=0" >> .env
mkdir -p "$SOURCE_MAIN_VOLUME"/"$LOG_FOLDER_NAME"
mkdir -p "$SOURCE_MAIN_VOLUME"/"$DATA_FOLDER_NAME"/FT
mkdir -p "$SOURCE_MAIN_VOLUME"/"$DATA_FOLDER_NAME"/APEC

sudo docker compose up airflow-init
<!-- Run the docker compose -->
sudo docker compose up -d



<!-- DEPRECATED IMAGE -->
https://docs.docker.com/engine/deprecated/
https://docs.docker.com/engine/deprecated/#pushing-and-pulling-with-image-manifest-v2-schema-1
https://docs.docker.com/config/daemon/systemd/
cat /etc/systemd/system/docker.service.d/override.conf
[Service]
Environment="DOCKER_ENABLE_DEPRECATED_PULL_SCHEMA_1_IMAGE=true"
sudo systemctl stop docker.service
sudo systemctl stop docker.socket
