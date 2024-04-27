# creation de l'image docker
sudo docker image build -t etl_extract:latest -f src/extract/Dockerfile .

# creation d'un volume ETL process
sudo docker volume create etl_process

# file_env file for container
DOWNLOAD_FOLDER=downloads/FT
SOURCE=0
PUBLIEEDEPUIS=1
ADDITIONAL_ARGUMENT=--department 13
FRANCE_EMPLOI_CLIENT_ID=PAR_jobmarketdatascientes_61aafad40553798b7d6198a1ece509eb5e20a3b1d239b478c3e09207209c9200
FRANCE_EMPLOI_CLIENT_SECRET=cdde83cbc9fb9d77ceb336af8d0dbacc1c11aaab3cd302f70792ab3c3a338e50

# Container creation
sudo docker container run \                                                                                                                                                                       !1531
    --rm \
    --env-file=file_env \
    -v etl_process:/project/downloads/FT \
    etl_extract:latest