# creation d'un volume ETL process
sudo docker volume create etl_process
#var/lib/docker/volumes/etl_process/_data
##########
# EXTRACT
##########
# creation de l'image docker
sudo docker image build -t etl_extract:latest -f src/extract/Dockerfile .

# file_env file for container
# DOWNLOAD_FOLDER=downloads/FT
# SOURCE=0
# PUBLIEEDEPUIS=1
# ADDITIONAL_ARGUMENT=--department 13
# FRANCE_EMPLOI_CLIENT_ID=PAR_jobmarketdatascientes_61aafad40553798b7d6198a1ece509eb5e20a3b1d239b478c3e09207209c9200
# FRANCE_EMPLOI_CLIENT_SECRET=cdde83cbc9fb9d77ceb336af8d0dbacc1c11aaab3cd302f70792ab3c3a338e50

# Container creation
sudo docker container run \
    --rm \
    --env-file=extract_file_env \
    -it \
    -v etl_volume:/project/downloads/FT \
    etl_extract:latest
    #    
    # etl_extract:latest

##########
# TRANSFORM
##########

sudo docker image build -t etl_transform:1.0.0 -f src/transform/Dockerfile .
# DOWNLOAD_FOLDER=downloads/FT
# SOURCE=0
sudo docker container run \
    -it \
    --rm \
    --env-file=transform_file_env \
    etl_transform:latest