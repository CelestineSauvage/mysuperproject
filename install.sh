# .pevn??
# prepare .env file

# creation des images
docker image build -t etl_extract:1.0.0 -f src/extract/Dockerfile .
docker image build -t etl_transform:1.0.0 -f src/transform/Dockerfile .
docker image build -t etl_load_into_db:1.0.0 -f src/load/Dockerfile .
docker image build --no-cache -t addcollection:1.0.0 -f src/addcollection/Dockerfile .
docker image build --no-cache -t jmfastapi:1.0.0 -f src/api/Dockerfile .
docker image build --no-cache -t jmdash:1.0.0 -f src/data_consumption/Dockerfile .