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
python3.12 -m venv .env 
```

- Activer l'environnement virtuel :
```shell script
source .env/bin/activate
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

## LANCEMENT DE LA RECUPERATION DES DONNES FRANCE TRAVAIL
```bash
python3 src/data_download.py downloads/France_Travail_22_04_24 --department 18  --publieeDepuis 1
```

## LANCEMENT DU SYSTEME DE GESTION DE BDD NOSQL MONGO DB
- Start mongodb and mongo-express contrainer

```shell script
sudo docker-compose up -d
```
