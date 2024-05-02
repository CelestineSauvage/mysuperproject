# .pevn??
# prepare .env file

# creation des images
docker image build -t etl_extract:1.0.0 -f src/extract/Dockerfile .
docker image build -t etl_transform:1.0.0 -f src/transform/Dockerfile .
docker image build -t etl_load_into_db:1.0.0 -f src/load/Dockerfile .
docker image build --no-cache -t addcollection:1.0.0 -f src/addcollection/Dockerfile .
docker image build --no-cache -t jmfastapi:1.0.0 -f src/api/Dockerfile .
docker image build --no-cache -t jmdash:1.0.0 -f src/data_consumption/Dockerfile .

# gestion partie airflow
# dans dossier principal
SOURCE_MAIN_VOLUME=/home/ubuntu/FEV24-BDE-JOBMARKET
LOG_FOLDER_NAME=logs_from_airflow
DATA_FOLDER_NAME=downloads_from_airflow/

mkdir -p "$SOURCE_MAIN_VOLUME"/"$LOG_FOLDER_NAME"
mkdir -p "$SOURCE_MAIN_VOLUME"/"$DATA_FOLDER_NAME"/FT
mkdir -p "$SOURCE_MAIN_VOLUME"/"$DATA_FOLDER_NAME"/APEC

# cd airflow
sudo docker compose up airflow-init

sudo docker compose up -d

